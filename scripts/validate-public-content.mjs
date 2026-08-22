import { readdir, readFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const root = process.cwd();
const forbiddenPathParts = new Set(['solucion', 'soluciones', 'solutions', 'answer-key']);
const forbiddenFiles = new Set(['cliente_multi_proveedor.py']);
const ignoredDirectories = new Set(['.git', '.venv', 'node_modules', '__pycache__']);
const violations = [];

async function walk(directory) {
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (ignoredDirectories.has(entry.name)) continue;
    const absolute = path.join(directory, entry.name);
    const relative = path.relative(root, absolute).split(path.sep).join('/');

    if (entry.isDirectory()) {
      if (forbiddenPathParts.has(entry.name.toLowerCase())) violations.push(relative);
      await walk(absolute);
      continue;
    }

    if (forbiddenFiles.has(entry.name.toLowerCase())) violations.push(relative);
    if (/\.(?:md|py|json)$/i.test(entry.name)) {
      const content = await readFile(absolute, 'utf8');
      if (/^public_solution\s*:\s*true\s*$/im.test(content)) violations.push(`${relative} (public_solution: true)`);
      if (/^#{1,3}\s+(?:Hoja de respuestas(?: explicada)?|Answer (?:sheet|key)(?: with explanations)?)\s*$/im.test(content)) violations.push(`${relative} (certification answer key)`);
      if (/^\*\*\d+\s+[—-]\s+[A-E]/im.test(content)) violations.push(`${relative} (reasoned answer row)`);
    }
  }
}

await walk(root);

if (violations.length) {
  console.error('Contenido de solución no permitido en el repositorio público:');
  for (const violation of [...new Set(violations)]) console.error(`- ${violation}`);
  process.exit(1);
}

console.log('Separación de soluciones verificada.');
