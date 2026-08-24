import assert from 'node:assert/strict';
import { execFile } from 'node:child_process';
import { createHash } from 'node:crypto';
import { mkdtemp, mkdir, readFile, symlink, writeFile } from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { promisify } from 'node:util';
import test from 'node:test';
import { fileURLToPath } from 'node:url';

import { validateCourseContracts } from '../validate-course-contracts.mjs';
import { validatePublicContent } from '../validate-public-content.mjs';

const repositoryRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const execFileAsync = promisify(execFile);

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

async function temporaryDirectory(prefix) {
  return mkdtemp(path.join(os.tmpdir(), prefix));
}

async function courseFixture(mutator = () => {}) {
  const root = await temporaryDirectory('llmec-course-');
  const spanish = JSON.parse(await readFile(path.join(repositoryRoot, 'course.json'), 'utf8'));
  const english = JSON.parse(await readFile(path.join(repositoryRoot, 'course.en.json'), 'utf8'));
  const schema = await readFile(path.join(repositoryRoot, 'course.schema.json'), 'utf8');
  mutator(spanish, english);
  await writeFile(path.join(root, 'course.json'), `${JSON.stringify(spanish, null, 2)}\n`);
  await writeFile(path.join(root, 'course.en.json'), `${JSON.stringify(english, null, 2)}\n`);
  await writeFile(path.join(root, 'course.schema.json'), schema);
  for (const relative of new Set([
    ...spanish.modules.map((module) => module.path),
    ...spanish.certifications.map((certification) => certification.sourcePath),
  ])) {
    if (!path.isAbsolute(relative) && !relative.split(/[\\/]/).includes('..')) {
      await mkdir(path.join(root, relative), { recursive: true });
    }
  }
  return root;
}

async function currentStackFixture({ reviewedAt, certifications = [] }) {
  const root = await temporaryDirectory('llmec-stack-');
  await writeFile(path.join(root, 'course.json'), `${JSON.stringify({ reviewedAt, certifications })}\n`);
  await writeFile(
    path.join(root, 'pyproject.toml'),
    '[project]\ndependencies = ["openai>=3,<4", "anthropic>=1,<2", "langgraph>=1.2,<2", "mcp[cli]>=2,<3"]\n',
  );
  const defaults = new Map([
    ['modulo-01-fundamentos-llm/labs/01_primer_llamada_openai.py', 'gpt-5.6-luna'],
    ['modulo-01-fundamentos-llm/labs/02_primer_llamada_anthropic.py', 'claude-haiku-4-5'],
    ['modulo-08-production-engineering/labs/04_model_routing.py', 'gpt-5.6-sol'],
  ]);
  for (const [relative, model] of defaults) {
    await mkdir(path.dirname(path.join(root, relative)), { recursive: true });
    await writeFile(path.join(root, relative), `CURRENT_MODEL = "${model}"\n`);
  }
  return root;
}

test('public-content validator accepts learning material that only mentions the private key', async () => {
  const root = await temporaryDirectory('llmec-public-clean-');
  await writeFile(path.join(root, 'README.md'), 'The reasoned answer key is kept outside this repository.\n');
  assert.deepEqual(await validatePublicContent({ root }), []);
});

test('public-content validator blocks answer-key files regardless of extension', async () => {
  const root = await temporaryDirectory('llmec-public-name-');
  await writeFile(path.join(root, 'answer-key.txt'), '1: A\n');
  assert.deepEqual(await validatePublicContent({ root }), ['answer-key.txt']);
});

test('public-content validator blocks disguised answer-key names and directories', async () => {
  const root = await temporaryDirectory('llmec-public-disguised-');
  await writeFile(path.join(root, 'notes.answer-key.en.md'), 'opaque\n');
  await mkdir(path.join(root, 'private-solutions'), { recursive: true });
  await writeFile(path.join(root, 'private-solutions/material.bin'), Buffer.from([1, 2, 3]));
  assert.deepEqual(await validatePublicContent({ root }), [
    'notes.answer-key.en.md',
    'private-solutions',
  ]);
});

test('public-content validator recognizes valid JSON solution markers', async () => {
  const root = await temporaryDirectory('llmec-public-json-');
  await writeFile(path.join(root, 'leak.json'), '{"public_solution": true, "answers": {"1": "A"}}\n');
  assert.deepEqual(await validatePublicContent({ root }), ['leak.json (public_solution: true)']);
});

test('public-content validator rejects symlinks instead of following content outside the repo', async () => {
  const root = await temporaryDirectory('llmec-public-link-');
  const outside = path.join(await temporaryDirectory('llmec-private-'), 'private.txt');
  await writeFile(outside, 'private editorial content\n');
  await symlink(outside, path.join(root, 'material.txt'));
  assert.deepEqual(await validatePublicContent({ root }), ['material.txt (enlace simbólico no permitido)']);
});

test('public-content validator scans tracked files even inside ignored tool directories', async () => {
  const root = await temporaryDirectory('llmec-public-tracked-');
  await execFileAsync('git', ['init', '--quiet'], { cwd: root });
  await writeFile(path.join(root, '.gitignore'), '.venv/\n');
  await mkdir(path.join(root, '.venv'), { recursive: true });
  await writeFile(path.join(root, '.venv/leak.txt'), 'public_solution: true\n');
  await execFileAsync('git', ['add', '--force', '.venv/leak.txt'], { cwd: root });
  assert.deepEqual(await validatePublicContent({ root }), ['.venv/leak.txt (public_solution: true)']);
});

test('course validator accepts the current complete contract', async () => {
  const root = await courseFixture();
  const result = await validateCourseContracts({ root });
  assert.equal(result.spanish.modules.length, result.english.modules.length);
});

test('course validator rejects impossible calendar dates', async () => {
  const root = await courseFixture((spanish, english) => {
    spanish.reviewedAt = '2099-99-99';
    english.reviewedAt = '2099-99-99';
  });
  await assert.rejects(validateCourseContracts({ root }), /fecha de calendario inválida/);
});

test('course validator rejects prerequisite cycles and forward dependencies', async () => {
  const root = await courseFixture((spanish, english) => {
    spanish.modules[0].prerequisites = ['module-02'];
    english.modules[0].prerequisites = ['module-02'];
  });
  await assert.rejects(validateCourseContracts({ root }), /debe preceder|Ciclo de prerrequisitos/);
});

test('course validator rejects paths that escape the repository', async () => {
  const root = await courseFixture((spanish, english) => {
    spanish.modules[0].path = '../private';
    english.modules[0].path = '../private';
  });
  await assert.rejects(validateCourseContracts({ root }), /ruta insegura/);
});

test('course validator requires HTTPS for published URLs', async () => {
  const root = await courseFixture((spanish, english) => {
    spanish.canonicalSite = 'http://llmengineerclub.com/es/';
    english.canonicalSite = 'http://llmengineerclub.com/';
  });
  await assert.rejects(validateCourseContracts({ root }), /debe usar HTTPS/);
});

test('current-stack validator rejects invalid and future review dates', async () => {
  const script = path.join(repositoryRoot, 'scripts/validate-current-stack.mjs');
  for (const reviewedAt of ['2026-02-30', '2099-99-99', '2999-01-01']) {
    const root = await currentStackFixture({ reviewedAt });
    await assert.rejects(
      execFileAsync(process.execPath, [script], { cwd: root, encoding: 'utf8' }),
      (error) => {
        assert.match(error.stderr, /fecha válida|futuro/);
        return true;
      },
    );
  }
});

test('translation pipeline never replaces a malformed manifest', async () => {
  const root = await temporaryDirectory('llmec-translation-');
  const manifest = path.join(root, 'translations/en/.translation-manifest.json');
  await mkdir(path.dirname(manifest), { recursive: true });
  await writeFile(path.join(root, 'README.md'), '# Fuente\n');
  await writeFile(manifest, '{not valid json\n');
  const script = path.join(repositoryRoot, 'scripts/translate-content.mjs');
  await assert.rejects(
    execFileAsync(process.execPath, [script, '--path', 'README.md'], { cwd: root, encoding: 'utf8' }),
    (error) => {
      assert.match(error.stderr, /no se sobrescribirá el historial/);
      return true;
    },
  );
  assert.equal(await readFile(manifest, 'utf8'), '{not valid json\n');
});

test('translation pipeline verifies the output hash before skipping a source', async () => {
  const root = await temporaryDirectory('llmec-translation-hash-');
  const source = '# Fuente\n';
  const translation = '# Source\n';
  const target = path.join(root, 'translations/en/README.md');
  const manifest = path.join(root, 'translations/en/.translation-manifest.json');
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(path.join(root, 'README.md'), source);
  await writeFile(target, translation);
  await writeFile(manifest, `${JSON.stringify({
    version: 1,
    model: 'offline-test',
    generatedAt: '2026-08-24T00:00:00.000Z',
    files: {
      'README.md': {
        sourceHash: sha256(source),
        translationHash: sha256(translation),
        model: 'offline-test',
        pipelineVersion: 2,
        translatedAt: '2026-08-24T00:00:00.000Z',
      },
    },
  }, null, 2)}\n`);
  const script = path.join(repositoryRoot, 'scripts/translate-content.mjs');
  const options = {
    cwd: root,
    encoding: 'utf8',
    env: { ...process.env, OLLAMA_URL: 'http://127.0.0.1:1' },
  };

  const skipped = await execFileAsync(process.execPath, [script, '--path', 'README.md'], options);
  assert.match(skipped.stdout, /sin cambios README\.md/);

  const tampered = '# Tampered\n';
  await writeFile(target, tampered);
  await assert.rejects(execFileAsync(process.execPath, [script, '--path', 'README.md'], options));
  assert.equal(await readFile(target, 'utf8'), tampered);
});
