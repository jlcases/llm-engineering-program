import { execFile } from 'node:child_process';
import { lstat, readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import { promisify } from 'node:util';
import { pathToFileURL } from 'node:url';

const execFileAsync = promisify(execFile);

const forbiddenPathNames = new Set([
  'answer-key',
  'answer_key',
  'answers',
  'respuesta',
  'respuestas',
  'solucion',
  'soluciones',
  'solution',
  'solutions',
]);
const forbiddenFiles = new Set(['cliente_multi_proveedor.py']);
const ignoredDirectories = new Set([
  '.git',
  '.mypy_cache',
  '.pytest_cache',
  '.ruff_cache',
  '.venv',
  '__pycache__',
  'node_modules',
]);
const maximumScannedBytes = 10 * 1024 * 1024;

function normalizedStem(name) {
  return path.basename(name, path.extname(name)).normalize('NFKC').toLocaleLowerCase('es');
}

function hasForbiddenPathName(name) {
  const canonical = name
    .normalize('NFKD')
    .replaceAll(/\p{M}/gu, '')
    .toLocaleLowerCase('es');
  return forbiddenPathNames.has(normalizedStem(canonical))
    || /(?:^|[._\s-])(?:answer[._\s-]*key|answers?|respuestas?|solucion(?:es)?|solutions?)(?:$|[._\s-])/u.test(canonical);
}

function contentViolations(content) {
  const findings = [];
  if (/^[\t ]*["']?public[_-]solution["']?[\t ]*[:=][\t ]*true\b/im.test(content)) {
    findings.push('public_solution: true');
  }
  if (/^#{1,3}\s+(?:Hoja de respuestas(?: explicada)?|Answer (?:sheet|key)(?: with explanations)?)\s*$/im.test(content)) {
    findings.push('certification answer key');
  }
  if (/^\*\*\d+\s+[—-]\s+[A-E]\b/im.test(content)) {
    findings.push('reasoned answer row');
  }
  return findings;
}

function containsPublicSolution(value) {
  if (Array.isArray(value)) return value.some(containsPublicSolution);
  if (!value || typeof value !== 'object') return false;
  return Object.entries(value).some(([key, child]) => (
    key.normalize('NFKC').toLocaleLowerCase('en').replaceAll('-', '_') === 'public_solution' && child === true
  ) || containsPublicSolution(child));
}

async function scanFile(absolute, relative, violations) {
  const buffer = await readFile(absolute);
  if (buffer.byteLength > maximumScannedBytes) {
    violations.push(`${relative} (archivo demasiado grande para verificar)`);
    return;
  }
  if (buffer.includes(0)) return;
  const content = buffer.toString('utf8');
  const findings = contentViolations(content);
  const extension = path.extname(relative).toLocaleLowerCase('en');
  if (extension === '.json' || extension === '.ipynb') {
    try {
      if (containsPublicSolution(JSON.parse(content))) findings.push('public_solution: true');
    } catch {
      // Other validators own syntax. The text signatures still run on malformed files.
    }
  } else if (extension === '.jsonl') {
    for (const line of content.split('\n').filter((candidate) => candidate.trim())) {
      try {
        if (containsPublicSolution(JSON.parse(line))) findings.push('public_solution: true');
      } catch {
        // Ignore malformed rows here; this validator is only responsible for solution leakage.
      }
    }
  }
  for (const finding of new Set(findings)) violations.push(`${relative} (${finding})`);
}

async function walk(root, directory, violations) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (ignoredDirectories.has(entry.name)) continue;
    const absolute = path.join(directory, entry.name);
    const relative = path.relative(root, absolute).split(path.sep).join('/');

    if (entry.isSymbolicLink()) {
      violations.push(`${relative} (enlace simbólico no permitido)`);
      continue;
    }
    if (entry.isDirectory()) {
      if (hasForbiddenPathName(entry.name)) {
        violations.push(relative);
      }
      await walk(root, absolute, violations);
      continue;
    }
    if (!entry.isFile()) {
      violations.push(`${relative} (tipo de entrada no verificable)`);
      continue;
    }
    if (forbiddenFiles.has(entry.name.toLocaleLowerCase('es')) || hasForbiddenPathName(entry.name)) {
      violations.push(relative);
    }
    await scanFile(absolute, relative, violations);
  }
}

async function scanTrackedIgnoredPaths(root, violations) {
  let stdout;
  try {
    ({ stdout } = await execFileAsync('git', ['-C', root, 'ls-files', '-z'], {
      encoding: 'utf8',
      maxBuffer: 64 * 1024 * 1024,
    }));
  } catch {
    return;
  }
  for (const relative of stdout.split('\0').filter(Boolean)) {
    const segments = relative.split('/');
    if (!segments.some((segment) => ignoredDirectories.has(segment))) continue;
    for (let index = 0; index < segments.length - 1; index += 1) {
      if (hasForbiddenPathName(segments[index])) {
        violations.push(segments.slice(0, index + 1).join('/'));
      }
    }
    const absolute = path.join(root, ...segments);
    const metadata = await lstat(absolute).catch(() => null);
    if (!metadata) continue;
    if (metadata.isSymbolicLink()) {
      violations.push(`${relative} (enlace simbólico no permitido)`);
      continue;
    }
    if (!metadata.isFile()) {
      violations.push(`${relative} (tipo de entrada no verificable)`);
      continue;
    }
    const name = segments.at(-1);
    if (forbiddenFiles.has(name.toLocaleLowerCase('es')) || hasForbiddenPathName(name)) {
      violations.push(relative);
    }
    await scanFile(absolute, relative, violations);
  }
}

export async function validatePublicContent({ root = process.cwd() } = {}) {
  const resolvedRoot = path.resolve(root);
  const violations = [];
  await walk(resolvedRoot, resolvedRoot, violations);
  await scanTrackedIgnoredPaths(resolvedRoot, violations);
  return [...new Set(violations)].sort();
}

async function main() {
  const violations = await validatePublicContent();
  if (violations.length) {
    console.error('Contenido de solución no permitido en el repositorio público:');
    for (const violation of violations) console.error(`- ${violation}`);
    process.exitCode = 1;
    return;
  }
  console.log('Separación de soluciones verificada.');
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  await main();
}
