import { readFile } from 'node:fs/promises';

const spanish = JSON.parse(await readFile('course.json', 'utf8'));
const english = JSON.parse(await readFile('course.en.json', 'utf8'));
const courseSchema = JSON.parse(await readFile('course.schema.json', 'utf8'));

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function resolveReference(reference) {
  assert(reference.startsWith('#/'), `Referencia de schema no soportada: ${reference}`);
  return reference.slice(2).split('/').reduce((value, segment) => value[segment.replace(/~1/g, '/').replace(/~0/g, '~')], courseSchema);
}

function validateSchema(schema, value, pointer, errors) {
  if (schema.$ref) return validateSchema(resolveReference(schema.$ref), value, pointer, errors);
  if ('const' in schema && value !== schema.const) errors.push(`${pointer}: debe ser ${JSON.stringify(schema.const)}`);
  if (schema.enum && !schema.enum.includes(value)) errors.push(`${pointer}: valor fuera del enum`);

  const actualType = Array.isArray(value) ? 'array' : value === null ? 'null' : Number.isInteger(value) ? 'integer' : typeof value;
  if (schema.type) {
    const matches = schema.type === actualType || (schema.type === 'number' && typeof value === 'number');
    if (!matches) { errors.push(`${pointer}: se esperaba ${schema.type} y llegó ${actualType}`); return; }
  }

  if (typeof value === 'string') {
    if (schema.minLength && value.length < schema.minLength) errors.push(`${pointer}: longitud menor que ${schema.minLength}`);
    if (schema.pattern && !new RegExp(schema.pattern).test(value)) errors.push(`${pointer}: no cumple ${schema.pattern}`);
    if (schema.format === 'uri') { try { new URL(value); } catch { errors.push(`${pointer}: URI inválida`); } }
    if (schema.format === 'date' && !/^\d{4}-\d{2}-\d{2}$/.test(value)) errors.push(`${pointer}: fecha inválida`);
  }
  if (typeof value === 'number') {
    if (schema.minimum !== undefined && value < schema.minimum) errors.push(`${pointer}: menor que ${schema.minimum}`);
    if (schema.maximum !== undefined && value > schema.maximum) errors.push(`${pointer}: mayor que ${schema.maximum}`);
    if (schema.exclusiveMinimum !== undefined && value <= schema.exclusiveMinimum) errors.push(`${pointer}: debe ser mayor que ${schema.exclusiveMinimum}`);
  }
  if (Array.isArray(value)) {
    if (schema.minItems && value.length < schema.minItems) errors.push(`${pointer}: necesita al menos ${schema.minItems} elementos`);
    if (schema.uniqueItems && new Set(value.map((item) => JSON.stringify(item))).size !== value.length) errors.push(`${pointer}: contiene duplicados`);
    if (schema.items) value.forEach((item, index) => validateSchema(schema.items, item, `${pointer}/${index}`, errors));
  }
  if (value && typeof value === 'object' && !Array.isArray(value)) {
    for (const required of schema.required ?? []) if (!(required in value)) errors.push(`${pointer}/${required}: propiedad obligatoria ausente`);
    const properties = schema.properties ?? {};
    if (schema.additionalProperties === false) for (const key of Object.keys(value)) if (!(key in properties)) errors.push(`${pointer}/${key}: propiedad adicional no permitida`);
    for (const [key, child] of Object.entries(value)) if (properties[key]) validateSchema(properties[key], child, `${pointer}/${key}`, errors);
  }
}

for (const [label, course] of [['course.json', spanish], ['course.en.json', english]]) {
  const errors = [];
  validateSchema(courseSchema, course, label, errors);
  assert(errors.length === 0, `Contrato inválido en ${label}:\n- ${errors.join('\n- ')}`);
}

assert(spanish.id === english.id, 'ES y EN deben describir el mismo curso.');
assert(spanish.modules.length === english.modules.length, 'ES y EN deben tener el mismo número de módulos.');
assert(spanish.competencies.length === english.competencies.length, 'ES y EN deben tener las mismas competencias.');
assert(spanish.certifications.length === english.certifications.length, 'ES y EN deben tener las mismas certificaciones.');

for (let index = 0; index < spanish.modules.length; index += 1) {
  assert(spanish.modules[index].id === english.modules[index].id, `Módulo desalineado en la posición ${index + 1}.`);
  assert(spanish.modules[index].slug === english.modules[index].sourceSlug, `sourceSlug EN incorrecto en ${english.modules[index].id}.`);
  assert(JSON.stringify(spanish.modules[index].prerequisites) === JSON.stringify(english.modules[index].prerequisites), `Prerequisitos desalineados en ${english.modules[index].id}.`);
  assert(JSON.stringify(spanish.modules[index].competencies) === JSON.stringify(english.modules[index].competencies), `Competencias desalineadas en ${english.modules[index].id}.`);
  assert(spanish.modules[index].ects === english.modules[index].ects, `ECTS desalineados en ${english.modules[index].id}.`);
}

assert(new Set(spanish.modules.map((module) => module.id)).size === spanish.modules.length, 'IDs de módulo duplicados.');
assert(new Set(spanish.competencies.map((competency) => competency.id)).size === spanish.competencies.length, 'IDs de competencia duplicados.');
assert(spanish.modules.reduce((sum, module) => sum + module.ects, 0) === spanish.ects, 'Los ECTS de los módulos no suman el total del curso.');
const moduleIds = new Set(spanish.modules.map((module) => module.id));
const competencyIds = new Set(spanish.competencies.map((competency) => competency.id));
for (const module of spanish.modules) {
  for (const prerequisite of module.prerequisites) assert(moduleIds.has(prerequisite), `Prerequisito inexistente en ${module.id}: ${prerequisite}`);
  for (const competency of module.competencies) assert(competencyIds.has(competency), `Competencia inexistente en ${module.id}: ${competency}`);
}

for (const certification of spanish.certifications) {
  const translated = english.certifications.find((candidate) => candidate.id === certification.id);
  assert(translated, `Falta certificación EN: ${certification.id}.`);
  assert(JSON.stringify(certification.exam) === JSON.stringify(translated.exam), `El contrato de examen difiere en ${certification.id}.`);
  assert(certification.domains.reduce((sum, domain) => sum + domain.weight, 0) === 100, `Los pesos no suman 100 en ${certification.id}.`);
  for (const domain of certification.domains) for (const moduleId of domain.modules) assert(moduleIds.has(moduleId), `Módulo inexistente en ${domain.id}: ${moduleId}`);
}

console.log('Contratos ES/EN alineados.');
