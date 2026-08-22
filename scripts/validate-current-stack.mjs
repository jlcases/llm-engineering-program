import { readFile, readdir } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const root = process.cwd();
const course = JSON.parse(await readFile('course.json', 'utf8'));
const pyproject = await readFile('pyproject.toml', 'utf8');
const failures = [];

function ageInDays(dateText) {
  return Math.floor((Date.now() - Date.parse(`${dateText}T00:00:00Z`)) / 86_400_000);
}

if (ageInDays(course.reviewedAt) > 120) failures.push(`course.reviewedAt lleva ${ageInDays(course.reviewedAt)} días sin revisión (máximo 120).`);
for (const certification of course.certifications) {
  if (ageInDays(certification.verifiedAt) > 180) failures.push(`${certification.code} lleva ${ageInDays(certification.verifiedAt)} días sin verificar (máximo 180).`);
}

const requiredDependencyContracts = [
  /"openai>=3(?:\.|,|<)/,
  /"anthropic>=1(?:\.|,|<)/,
  /"langgraph>=1\.2(?:\.|,|<)/,
  /"mcp\[cli\]>=2(?:\.|,|<)/,
];
for (const pattern of requiredDependencyContracts) if (!pattern.test(pyproject)) failures.push(`pyproject.toml no cumple ${pattern}.`);

async function walk(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (['.git', '.venv', 'translations', '__pycache__', 'node_modules'].includes(entry.name)) continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await walk(absolute));
    else if (entry.name.endsWith('.py')) files.push(absolute);
  }
  return files;
}

async function walkCurrentSources(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (['.git', '.venv', 'translations', '__pycache__', 'node_modules'].includes(entry.name)) continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await walkCurrentSources(absolute));
    else if (/\.(?:md|ya?ml)$/.test(entry.name)) files.push(absolute);
  }
  return files;
}

const staleDefault = /(?:^|\n)\s*(?:[A-Z_]*MODEL|model)\s*=\s*(?:os\.getenv\([^,]+,\s*)?["'](?:gpt-(?:3|4)(?:\.|-|["'])|claude-(?:2|3)(?:\.|-|["'])|gemini-(?:1|2)(?:\.|-|["'])|llama[-_ ]?3(?:\.|-|["']))/i;
for (const file of await walk(root)) {
  const source = await readFile(file, 'utf8');
  if (staleDefault.test(source)) failures.push(`${path.relative(root, file)} fija un modelo legacy como default.`);
  if (/from openai import OpenAI/.test(source) && !/\.responses\.(?:create|parse)\(/.test(source)) failures.push(`${path.relative(root, file)} usa OpenAI sin Responses API.`);
}

const staleActions = [
  [/actions\/checkout@v[1-6]\b/, 'actions/checkout debe usar v7'],
  [/actions\/setup-node@v[1-6]\b/, 'actions/setup-node debe usar v7'],
  [/actions\/setup-python@v[1-6]\b/, 'actions/setup-python debe usar v7'],
  [/astral-sh\/setup-uv@v[1-9]\b/, 'astral-sh/setup-uv debe usar v10'],
];
for (const file of await walkCurrentSources(root)) {
  const source = await readFile(file, 'utf8');
  for (const [pattern, message] of staleActions) {
    if (pattern.test(source)) failures.push(`${path.relative(root, file)}: ${message}.`);
  }
}

const requiredDefaults = new Map([
  ['modulo-01-fundamentos-llm/labs/01_primer_llamada_openai.py', 'gpt-5.6-luna'],
  ['modulo-01-fundamentos-llm/labs/02_primer_llamada_anthropic.py', 'claude-haiku-4-5'],
  ['modulo-05-llmops/labs/04_model_routing.py', 'gpt-5.6-sol'],
]);
for (const [file, model] of requiredDefaults) {
  const source = await readFile(file, 'utf8');
  if (!source.includes(model)) failures.push(`${file} no contiene el default vigente ${model}.`);
}

if (failures.length) {
  console.error(`Stack desactualizado o sin contrato (${failures.length}):\n- ${failures.join('\n- ')}`);
  process.exit(1);
}
console.log(`Stack vigente verificado. Revisión del curso: ${course.reviewedAt}.`);
