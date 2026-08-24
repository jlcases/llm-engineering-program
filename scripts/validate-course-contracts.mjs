import { readFile, stat } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { pathToFileURL } from 'node:url';

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function resolveReference(reference, schemaRoot) {
  assert(reference.startsWith('#/'), `Referencia de schema no soportada: ${reference}`);
  return reference.slice(2).split('/').reduce((value, segment) => {
    assert(value && typeof value === 'object', `Referencia de schema inexistente: ${reference}`);
    return value[segment.replace(/~1/g, '/').replace(/~0/g, '~')];
  }, schemaRoot);
}

function parseIsoDate(value) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (!match) return null;
  const [, yearText, monthText, dayText] = match;
  const year = Number(yearText);
  const month = Number(monthText);
  const day = Number(dayText);
  const timestamp = Date.UTC(year, month - 1, day);
  const date = new Date(timestamp);
  if (date.getUTCFullYear() !== year || date.getUTCMonth() !== month - 1 || date.getUTCDate() !== day) return null;
  return date;
}

function validateSchema(schema, value, pointer, errors, schemaRoot) {
  if (schema.$ref) return validateSchema(resolveReference(schema.$ref, schemaRoot), value, pointer, errors, schemaRoot);
  if ('const' in schema && value !== schema.const) errors.push(`${pointer}: debe ser ${JSON.stringify(schema.const)}`);
  if (schema.enum && !schema.enum.includes(value)) errors.push(`${pointer}: valor fuera del enum`);

  const actualType = Array.isArray(value) ? 'array' : value === null ? 'null' : Number.isInteger(value) ? 'integer' : typeof value;
  if (schema.type) {
    const matches = schema.type === actualType || (schema.type === 'number' && typeof value === 'number' && Number.isFinite(value));
    if (!matches) { errors.push(`${pointer}: se esperaba ${schema.type} y llegó ${actualType}`); return; }
  }

  if (typeof value === 'string') {
    if (schema.minLength !== undefined && value.length < schema.minLength) errors.push(`${pointer}: longitud menor que ${schema.minLength}`);
    if (schema.pattern && !new RegExp(schema.pattern, 'u').test(value)) errors.push(`${pointer}: no cumple ${schema.pattern}`);
    if (schema.format === 'uri') {
      try {
        const url = new URL(value);
        if (url.protocol !== 'https:') errors.push(`${pointer}: la URI debe usar HTTPS`);
      } catch {
        errors.push(`${pointer}: URI inválida`);
      }
    }
    if (schema.format === 'date' && !parseIsoDate(value)) errors.push(`${pointer}: fecha de calendario inválida`);
  }
  if (typeof value === 'number') {
    if (!Number.isFinite(value)) errors.push(`${pointer}: número no finito`);
    if (schema.minimum !== undefined && value < schema.minimum) errors.push(`${pointer}: menor que ${schema.minimum}`);
    if (schema.maximum !== undefined && value > schema.maximum) errors.push(`${pointer}: mayor que ${schema.maximum}`);
    if (schema.exclusiveMinimum !== undefined && value <= schema.exclusiveMinimum) errors.push(`${pointer}: debe ser mayor que ${schema.exclusiveMinimum}`);
  }
  if (Array.isArray(value)) {
    if (schema.minItems !== undefined && value.length < schema.minItems) errors.push(`${pointer}: necesita al menos ${schema.minItems} elementos`);
    if (schema.uniqueItems && new Set(value.map((item) => JSON.stringify(item))).size !== value.length) errors.push(`${pointer}: contiene duplicados`);
    if (schema.items) value.forEach((item, index) => validateSchema(schema.items, item, `${pointer}/${index}`, errors, schemaRoot));
  }
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    for (const required of schema.required ?? []) if (!(required in value)) errors.push(`${pointer}/${required}: propiedad obligatoria ausente`);
    const properties = schema.properties ?? {};
    if (schema.additionalProperties === false) for (const key of Object.keys(value)) if (!(key in properties)) errors.push(`${pointer}/${key}: propiedad adicional no permitida`);
    for (const [key, child] of Object.entries(value)) if (properties[key]) validateSchema(properties[key], child, `${pointer}/${key}`, errors, schemaRoot);
  }
}

function assertUnique(values, message) {
  assert(new Set(values).size === values.length, message);
}

function assertPastOrToday(value, label) {
  const date = parseIsoDate(value);
  assert(date, `${label}: fecha de calendario inválida`);
  const now = new Date();
  const today = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
  assert(date.getTime() <= today, `${label}: la fecha no puede estar en el futuro`);
}

async function assertSafeExistingPath(root, relative, label) {
  assert(typeof relative === 'string' && relative.length > 0, `${label}: ruta vacía`);
  assert(!path.isAbsolute(relative) && !relative.split(/[\\/]/).includes('..'), `${label}: ruta insegura`);
  const absolute = path.resolve(root, relative);
  assert(absolute.startsWith(`${root}${path.sep}`), `${label}: ruta fuera del repositorio`);
  const metadata = await stat(absolute).catch(() => null);
  assert(metadata, `${label}: no existe ${relative}`);
  assert(metadata.isDirectory() || metadata.isFile(), `${label}: tipo de ruta no soportado`);
}

function assertAcyclicPrerequisites(modules) {
  const byId = new Map(modules.map((module) => [module.id, module]));
  const visiting = new Set();
  const visited = new Set();
  function visit(moduleId, trail) {
    if (visiting.has(moduleId)) throw new Error(`Ciclo de prerrequisitos: ${[...trail, moduleId].join(' -> ')}`);
    if (visited.has(moduleId)) return;
    visiting.add(moduleId);
    const module = byId.get(moduleId);
    for (const prerequisite of module.prerequisites) visit(prerequisite, [...trail, moduleId]);
    visiting.delete(moduleId);
    visited.add(moduleId);
  }
  for (const module of modules) visit(module.id, []);
}

export async function validateCourseContracts({ root = process.cwd() } = {}) {
  const resolvedRoot = path.resolve(root);
  const spanish = JSON.parse(await readFile(path.join(resolvedRoot, 'course.json'), 'utf8'));
  const english = JSON.parse(await readFile(path.join(resolvedRoot, 'course.en.json'), 'utf8'));
  const courseSchema = JSON.parse(await readFile(path.join(resolvedRoot, 'course.schema.json'), 'utf8'));

  for (const [label, course] of [['course.json', spanish], ['course.en.json', english]]) {
    const errors = [];
    validateSchema(courseSchema, course, label, errors, courseSchema);
    assert(errors.length === 0, `Contrato inválido en ${label}:\n- ${errors.join('\n- ')}`);
  }

  assert(spanish.id === english.id, 'ES y EN deben describir el mismo curso.');
  assert(spanish.language === 'es' && english.language === 'en', 'Los idiomas declarados deben ser ES y EN.');
  assert(
    JSON.stringify([...spanish.availableLanguages].sort()) === JSON.stringify([...english.availableLanguages].sort()),
    'Los idiomas disponibles difieren entre ES y EN.',
  );
  assertPastOrToday(spanish.reviewedAt, 'course.reviewedAt');
  assertPastOrToday(english.reviewedAt, 'course.en.reviewedAt');

  const alignedCollections = [
    ['módulos', spanish.modules, english.modules],
    ['competencias', spanish.competencies, english.competencies],
    ['certificaciones', spanish.certifications, english.certifications],
  ];
  for (const [label, left, right] of alignedCollections) {
    assert(left.length === right.length, `ES y EN deben tener el mismo número de ${label}.`);
    assert(JSON.stringify(left.map((item) => item.id)) === JSON.stringify(right.map((item) => item.id)), `IDs u orden de ${label} desalineados entre ES y EN.`);
  }

  for (let index = 0; index < spanish.modules.length; index += 1) {
    const source = spanish.modules[index];
    const translated = english.modules[index];
    assert(source.slug === translated.sourceSlug, `sourceSlug EN incorrecto en ${translated.id}.`);
    assert(JSON.stringify(source.prerequisites) === JSON.stringify(translated.prerequisites), `Prerequisitos desalineados en ${translated.id}.`);
    assert(JSON.stringify(source.competencies) === JSON.stringify(translated.competencies), `Competencias desalineadas en ${translated.id}.`);
    assert(JSON.stringify(source.effortHours) === JSON.stringify(translated.effortHours), `Esfuerzo desalineado en ${translated.id}.`);
    assert(source.number === index + 1 && translated.number === index + 1, `Numeración no secuencial en ${source.id}.`);
    assert(source.effortHours.min <= source.effortHours.max, `Rango de esfuerzo invertido en ${source.id}.`);
  }

  assertUnique(spanish.modules.map((module) => module.id), 'IDs de módulo duplicados.');
  assertUnique(spanish.modules.map((module) => module.slug), 'Slugs de módulo duplicados.');
  assertUnique(spanish.modules.map((module) => module.path), 'Paths de módulo duplicados.');
  assertUnique(spanish.competencies.map((competency) => competency.id), 'IDs de competencia duplicados.');
  assertUnique(spanish.certifications.map((certification) => certification.id), 'IDs de certificación duplicados.');
  assertUnique(spanish.certifications.map((certification) => certification.code), 'Códigos de certificación duplicados.');

  const summedEffort = spanish.modules.reduce(
    (total, module) => ({ min: total.min + module.effortHours.min, max: total.max + module.effortHours.max }),
    { min: 0, max: 0 },
  );
  assert(JSON.stringify(summedEffort) === JSON.stringify(spanish.effortHours), 'El esfuerzo estimado de los módulos no suma el total de la ruta.');
  assert(JSON.stringify(spanish.effortHours) === JSON.stringify(english.effortHours), 'El esfuerzo total difiere entre ES y EN.');

  const moduleIds = new Set(spanish.modules.map((module) => module.id));
  const competencyIds = new Set(spanish.competencies.map((competency) => competency.id));
  const moduleNumbers = new Map(spanish.modules.map((module) => [module.id, module.number]));
  for (const module of spanish.modules) {
    for (const prerequisite of module.prerequisites) {
      assert(moduleIds.has(prerequisite), `Prerequisito inexistente en ${module.id}: ${prerequisite}`);
      assert(moduleNumbers.get(prerequisite) < module.number, `El prerrequisito ${prerequisite} debe preceder a ${module.id}.`);
    }
    for (const competency of module.competencies) assert(competencyIds.has(competency), `Competencia inexistente en ${module.id}: ${competency}`);
    await assertSafeExistingPath(resolvedRoot, module.path, `Path de ${module.id}`);
  }
  assertAcyclicPrerequisites(spanish.modules);

  for (const certification of spanish.certifications) {
    const translated = english.certifications.find((candidate) => candidate.id === certification.id);
    assert(JSON.stringify(certification.exam) === JSON.stringify(translated.exam), `El contrato de examen difiere en ${certification.id}.`);
    assert(certification.domains.reduce((sum, domain) => sum + domain.weight, 0) === 100, `Los pesos no suman 100 en ${certification.id}.`);
    assertUnique(certification.domains.map((domain) => domain.id), `Dominios duplicados en ${certification.id}.`);
    assertPastOrToday(certification.verifiedAt, `${certification.code}.verifiedAt`);
    await assertSafeExistingPath(resolvedRoot, certification.sourcePath, `sourcePath de ${certification.id}`);
    for (const domain of certification.domains) {
      for (const moduleId of domain.modules) assert(moduleIds.has(moduleId), `Módulo inexistente en ${domain.id}: ${moduleId}`);
    }
  }
  return { spanish, english };
}

async function main() {
  await validateCourseContracts();
  console.log('Contratos ES/EN alineados.');
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  await main();
}
