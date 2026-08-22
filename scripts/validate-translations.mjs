import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { readFile, readdir, stat } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const root = process.cwd();
const outputRoot = path.join(root, 'translations/en');
const manifest = JSON.parse(await readFile(path.join(outputRoot, '.translation-manifest.json'), 'utf8'));
const ignored = new Set(['.git', '.venv', 'node_modules', '__pycache__', 'translations']);
const strict = process.argv.includes('--complete') || process.env.REQUIRE_COMPLETE_TRANSLATIONS === '1';
const pathIndex = process.argv.indexOf('--path');
const selectedPath = pathIndex >= 0 ? process.argv[pathIndex + 1] : null;

if (selectedPath && (path.isAbsolute(selectedPath) || selectedPath.split(/[\\/]/).includes('..'))) {
  throw new Error('Usa --path con una ruta relativa segura.');
}

const sha256 = (value) => createHash('sha256').update(value).digest('hex');

async function walk(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (ignored.has(entry.name) || entry.name.startsWith('.')) continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await walk(absolute));
    else files.push(path.relative(root, absolute).split(path.sep).join('/'));
  }
  return files;
}

function isPublishable(sourcePath) {
  const extension = path.extname(sourcePath);
  if (extension !== '.md' && extension !== '.py') return false;
  if (extension === '.py' && (!sourcePath.includes('/labs/') || path.posix.basename(sourcePath).startsWith('_'))) return false;
  return sourcePath === 'README.md'
    || sourcePath === 'PLAN_DE_ESTUDIOS.md'
    || sourcePath.startsWith('modulo-')
    || sourcePath.startsWith('certificaciones/')
    || sourcePath === 'recursos/README.md'
    || sourcePath === 'setup/README.md';
}

function pythonAstWithoutDocstrings(filePath) {
  const program = String.raw`import ast, sys
p=sys.argv[1]
tree=ast.parse(open(p, encoding='utf-8').read(), filename=p)
for node in ast.walk(tree):
    body=getattr(node, 'body', None)
    if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        node.body=body[1:]
print(ast.dump(tree, annotate_fields=True, include_attributes=False))`;
  return execFileSync('python3', ['-c', program, filePath], { encoding: 'utf8', maxBuffer: 16 * 1024 * 1024 });
}

function markdownArtifacts(source) {
  const fences = source.match(/^```[^\n]*\n[\s\S]*?^```[ \t]*$/gm) ?? [];
  const prose = source.replace(/^```[^\n]*\n[\s\S]*?^```[ \t]*$/gm, 'LLMEC_FENCE');
  return {
    fences: fences.map(fenceArtifact),
    headings: prose.match(/^#{1,6}\s+/gm) ?? [],
    strongMarkers: (prose.match(/\*\*/g) ?? []).length,
    inline: prose.match(/(?<!`)(`+)(?!`)([^\n]*?)\1(?!`)/g) ?? [],
    links: [...prose.matchAll(/\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g)].map((match) => linkArtifact(match[1])),
    lists: [...prose.matchAll(/^([ \t]*)([-*+]|\d+[.)])[ \t]+/gm)].map((match) => `${match[1].length}:${match[2]}`),
    blockquotes: prose.match(/^[ \t]*>[ \t]?/gm) ?? [],
    tablePipes: prose.split('\n').filter((line) => (line.match(/\|/g) ?? []).length >= 2).map((line) => (line.match(/\|/g) ?? []).length),
    blankRuns: prose.match(/\n{2,}/g)?.map((run) => run.length) ?? [],
  };
}

function linkArtifact(href) {
  if (!/^https:\/\/llmengineerclub\.com\//.test(href)) return href;
  const url = new URL(href);
  url.pathname = url.pathname
    .replace(/^\/es\//, '/')
    .replace(/^\/certificaciones\//, '/certifications/')
    .replace(/\/simulacro\/$/, '/mock-exam/');
  return url.toString();
}

function fenceArtifact(fence) {
  if (!/^```mermaid\s*$/m.test(fence.split('\n', 1)[0])) return fence;
  const stateDiagram = /^```mermaid\s*\n\s*stateDiagram/m.test(fence);
  const nodes = new Map();
  const node = (value) => {
    if (value === '[*]') return value;
    if (!nodes.has(value)) nodes.set(value, `NODE_${nodes.size + 1}`);
    return nodes.get(value);
  };
  return fence.split('\n').map((line) => {
    let normalized = line
    .replace(/"[^"]*"/g, '"LABEL"')
    .replace(/\[[^\]]*\]/g, '[LABEL]')
    .replace(/\(\([^)]*\)\)/g, '((LABEL))')
    .replace(/\([^)]*\)/g, '(LABEL)')
    .replace(/\{[^}]*\}/g, '{LABEL}')
    .replace(/\|[^|\n]*\|/g, '|LABEL|')
    .replace(/-\..*?\.->/g, '-.LABEL.->')
    .replace(/--\s+.*?\s+-->/g, '-- LABEL -->')
    .replace(/^(\s*participant\s+\S+\s+as\s+).+$/i, '$1LABEL')
    .replace(/^((?:\s*Note\s+over\s+\S+|\s*\S+--?>>?\S+)\s*:).+$/i, '$1 LABEL')
    .replace(/^(\s*\S+\s+-->\s+\S+\s*:).+$/i, '$1 LABEL')
    .replace(/^(\s*(?:title|x-axis|y-axis))\s+.+$/i, '$1 LABEL')
    .replace(/^(\s*subgraph)\s+.+$/i, '$1 LABEL');
    if (stateDiagram) {
      const edge = normalized.match(/^(\s*)(\S+)\s+-->\s+(\S+)(.*)$/);
      if (edge) normalized = `${edge[1]}${node(edge[2])} --> ${node(edge[3])}${edge[4]}`;
    }
    return normalized;
  })
    .join('\n');
}

const spanishSignals = new Set(
  'el la los las una unas uno unos que para con sin por desde hasta aunque pero también cuando donde porque esto esta este estos estas sus más menos entre sobre siempre nunca ejecuta usa usar respuesta pregunta ejercicio ejercicios evaluación salida entrada código cada debe debes puede puedes hacer muestra después antes mismo misma archivo fichero devuelve añade contiene resultado campos claves tipos esquema errores texto herramienta herramientas usuario curso criterios'.split(' '),
);

function englishQualityProblem(markdown) {
  const prose = markdown
    .replace(/^```.*$[\s\S]*?^```\s*$/gm, ' ')
    .replace(/(?<!`)(`+)(?!`)([^\n]*?)\1(?!`)/g, ' ')
    .replace(/https?:\/\/[^\s)>]+/g, ' ');
  const allWords = prose.toLocaleLowerCase('es').match(/[\p{L}]+/gu) ?? [];
  let totalSignals = 0;
  for (const block of prose.split(/\n{2,}/)) {
    const words = block.toLocaleLowerCase('es').match(/[\p{L}]+/gu) ?? [];
    const signals = words.filter((word) => spanishSignals.has(word)).length;
    totalSignals += signals;
    if ((words.length >= 8 && signals >= 4 && signals / words.length >= 0.08)
      || (words.length >= 4 && signals >= 3 && signals / words.length >= 0.4)) {
      return `segmento con ${signals}/${words.length} señales de español`;
    }
  }
  if (totalSignals >= 12 && totalSignals / Math.max(allWords.length, 1) >= 0.02) {
    return `documento con ${totalSignals}/${allWords.length} señales de español`;
  }
  return null;
}

let paths = (await walk(root)).filter(isPublishable).sort();
if (selectedPath) {
  paths = paths.filter((sourcePath) => sourcePath === selectedPath);
  if (!paths.length) throw new Error(`No existe una fuente publicable: ${selectedPath}`);
}
const missing = [];
const problems = [];

for (const sourcePath of paths) {
  const sourceFile = path.join(root, sourcePath);
  const target = path.join(outputRoot, sourcePath);
  if (!(await stat(target).catch(() => null))?.isFile()) { missing.push(sourcePath); continue; }
  const source = await readFile(sourceFile, 'utf8');
  const translation = await readFile(target, 'utf8');
  const record = manifest.files[sourcePath];
  if (!record) problems.push(`${sourcePath}: falta en .translation-manifest.json`);
  else {
    if (record.sourceHash !== sha256(source)) problems.push(`${sourcePath}: traducción obsoleta respecto a la fuente`);
    if (record.translationHash !== sha256(translation)) problems.push(`${sourcePath}: hash de traducción alterado`);
    if (sourcePath.endsWith('.md') && record.pipelineVersion !== 2) problems.push(`${sourcePath}: requiere pipeline Markdown segmentado v2`);
  }
  if (/LLMEC_(?:FENCED|INLINE|LINK|URL)_|⟦LLMEC-[A-F]⟧/.test(translation)) problems.push(`${sourcePath}: contiene marcadores internos`);
  if (sourcePath.endsWith('.py')) {
    try {
      if (pythonAstWithoutDocstrings(sourceFile) !== pythonAstWithoutDocstrings(target)) problems.push(`${sourcePath}: cambió el AST fuera de docstrings`);
    } catch (error) {
      problems.push(`${sourcePath}: Python inválido (${error instanceof Error ? error.message : error})`);
    }
  } else {
    const before = markdownArtifacts(source);
    const after = markdownArtifacts(translation);
    const changed = Object.keys(before).filter((key) => JSON.stringify(before[key]) !== JSON.stringify(after[key]));
    if (changed.length) problems.push(`${sourcePath}: cambió estructura Markdown (${changed.join(', ')})`);
    const qualityProblem = englishQualityProblem(translation);
    if (qualityProblem) problems.push(`${sourcePath}: traducción inglesa parcial (${qualityProblem})`);
  }
}

if (!selectedPath) {
  for (const recordedPath of Object.keys(manifest.files)) {
    if (!paths.includes(recordedPath)) problems.push(`${recordedPath}: registro huérfano en el manifiesto`);
  }
}

if (problems.length || (strict && missing.length)) {
  if (problems.length) console.error(`Problemas de integridad EN (${problems.length}):\n- ${problems.join('\n- ')}`);
  if (strict && missing.length) console.error(`Traducciones ausentes (${missing.length}):\n- ${missing.join('\n- ')}`);
  process.exit(1);
}

const completed = paths.length - missing.length;
console.log(`Traducciones verificadas: ${completed}/${paths.length} (${Math.round(completed / paths.length * 10000) / 100}%).${missing.length ? ` Faltan ${missing.length}; usa --complete para exigir cobertura total.` : ''}`);
