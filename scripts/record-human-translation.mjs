import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdir, readFile, rm, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const index = process.argv.indexOf('--path');
const sourcePath = index >= 0 ? process.argv[index + 1] : null;
if (!sourcePath || path.isAbsolute(sourcePath) || sourcePath.split(/[\\/]/).includes('..')) {
  throw new Error('Usa --path con una ruta relativa segura, por ejemplo modulo-02-prompt-engineering/README.md.');
}

const root = process.cwd();
const sourceFile = path.join(root, sourcePath);
const translationFile = path.join(root, 'translations/en', sourcePath);
const manifestPath = path.join(root, 'translations/en/.translation-manifest.json');
const manifestLockPath = path.join(root, 'translations/en/.translation-manifest.lock');
if (!(await stat(sourceFile).catch(() => null))?.isFile()) throw new Error(`No existe la fuente: ${sourcePath}`);
if (!(await stat(translationFile).catch(() => null))?.isFile()) throw new Error(`No existe la traducción: translations/en/${sourcePath}`);

const sha256 = (value) => createHash('sha256').update(value).digest('hex');
const source = await readFile(sourceFile, 'utf8');
const translation = await readFile(translationFile, 'utf8');

async function acquireManifestLock() {
  for (let attempt = 0; attempt < 1200; attempt += 1) {
    try {
      await mkdir(manifestLockPath);
      return async () => rm(manifestLockPath, { recursive: true, force: true });
    } catch (error) {
      if (error?.code !== 'EEXIST') throw error;
      const lockStat = await stat(manifestLockPath).catch(() => null);
      if (lockStat && Date.now() - lockStat.mtimeMs > 60_000) {
        await rm(manifestLockPath, { recursive: true, force: true });
        continue;
      }
      await new Promise((resolve) => setTimeout(resolve, 50));
    }
  }
  throw new Error('Timeout esperando el manifiesto de traducción.');
}

const release = await acquireManifestLock();
const originalManifest = await readFile(manifestPath, 'utf8');
const manifest = JSON.parse(originalManifest);
manifest.files[sourcePath] = {
  sourceHash: sha256(source),
  translationHash: sha256(translation),
  model: 'human-reviewed',
  editor: process.env.GITHUB_ACTOR || process.env.USER || null,
  pipelineVersion: sourcePath.endsWith('.md') ? 2 : 1,
  translatedAt: new Date().toISOString(),
};
manifest.generatedAt = new Date().toISOString();
await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);

try {
  execFileSync(process.execPath, ['scripts/validate-translations.mjs', '--path', sourcePath], { cwd: root, stdio: 'inherit' });
} catch {
  await writeFile(manifestPath, originalManifest);
  throw new Error('La traducción no conserva el contrato estructural; corrige el fichero y vuelve a registrarlo.');
} finally {
  await release();
}
console.log(`Traducción humana registrada: ${sourcePath}`);
