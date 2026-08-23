import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdir, readFile, readdir, rename, rm, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';

const root = process.cwd();
const outputRoot = path.join(root, 'translations/en');
const manifestPath = path.join(outputRoot, '.translation-manifest.json');
const manifestLockPath = path.join(outputRoot, '.translation-manifest.lock');
const model = process.env.OLLAMA_TRANSLATION_MODEL || 'qwen3.6:35b-a3b-coding-nvfp4';
const endpoint = process.env.OLLAMA_URL || 'http://127.0.0.1:11434';
const selectedPath = valueAfter('--path');
const limit = Number(valueAfter('--limit') || 0);
const shardValue = valueAfter('--shard');
const force = process.argv.includes('--force');
const publishableExtensions = new Set(['.md', '.py']);
const ignored = new Set(['.git', '.venv', 'node_modules', '__pycache__', 'translations']);

function valueAfter(flag) {
  const index = process.argv.indexOf(flag);
  return index >= 0 ? process.argv[index + 1] : null;
}

function sha256(value) {
  return createHash('sha256').update(value).digest('hex');
}

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
  if (!publishableExtensions.has(extension)) return false;
  if (extension === '.py' && (!sourcePath.includes('/labs/') || path.posix.basename(sourcePath).startsWith('_'))) return false;
  return sourcePath === 'README.md'
    || sourcePath === 'RUTA_DE_APRENDIZAJE.md'
    || sourcePath.startsWith('modulo-')
    || sourcePath.startsWith('certificaciones/')
    || sourcePath === 'recursos/README.md'
    || sourcePath === 'setup/README.md';
}

function protectMarkdown(source) {
  const values = [];
  const placeholderCodes = { FENCED: 'A', INLINE: 'B', LINK: 'C', URL: 'D', QUOTE: 'E', STRONG: 'F' };
  const reserve = (value, kind) => {
    // Reusing one opaque token per construct avoids models "correcting" long
    // numeric identifiers. Values are restored in occurrence order per kind.
    const token = `⟦LLMEC-${placeholderCodes[kind]}⟧`;
    values.push({ token, value, kind });
    return token;
  };
  let protectedSource = source
    .replace(/^```[^\n]*\n[\s\S]*?^```[ \t]*$/gm, (value) => reserve(value, 'FENCED'))
    .replace(/(?<!`)(`+)(?!`)([^\n]*?)\1(?!`)/g, (value) => reserve(value, 'INLINE'))
    .replace(/\]\(([^)\s]+)(\s+"[^"]*")?\)/g, (_whole, target, title = '') => `](${reserve(target, 'LINK')}${title})`)
    .replace(/https?:\/\/[^\s)>]+/g, (value) => reserve(value, 'URL'))
    .replace(/^[ \t]*>[ \t]?/gm, (value) => reserve(value, 'QUOTE'))
    .replace(/\*\*/g, (value) => reserve(value, 'STRONG'));
  return {
    source: protectedSource,
    restore(translated) {
      for (const kind of Object.keys(placeholderCodes)) {
        const entries = values.filter((entry) => entry.kind === kind);
        if (!entries.length) continue;
        const token = entries[0].token;
        if (kind === 'INLINE') translated = translated.replaceAll(`\`${token}\``, token);
        const matches = translated.split(token).length - 1;
        if (matches !== entries.length) throw new Error(`Marcador alterado: ${token} aparece ${matches}/${entries.length} veces.`);
        let entryIndex = 0;
        translated = translated.replaceAll(token, () => entries[entryIndex++].value);
      }
      if (/⟦LLMEC-[A-F]⟧/.test(translated)) throw new Error('Quedan marcadores sin restaurar.');
      return translated;
    },
  };
}

function cleanModelOutput(value) {
  let output = value.trim();
  output = output.replace(/^<think>[\s\S]*?<\/think>\s*/i, '');
  const wrapped = output.match(/^```(?:markdown|md|python)?\s*\n([\s\S]*)\n```$/i);
  if (wrapped) output = wrapped[1];
  return `${output.trim()}\n`;
}

async function generate(prompt, json = false, seedOffset = 0) {
  const response = await fetch(`${endpoint}/api/generate`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    signal: AbortSignal.timeout(10 * 60 * 1000),
    body: JSON.stringify({
      model,
      prompt,
      stream: true,
      think: false,
      keep_alive: '30m',
      ...(json ? { format: 'json' } : {}),
      options: { temperature: 0.05, top_p: 0.9, num_ctx: 32768, num_predict: -1, seed: 20260821 + seedOffset },
    }),
  });
  if (!response.ok) throw new Error(`Ollama respondió ${response.status}: ${await response.text()}`);
  const chunks = (await response.text()).trim().split('\n').filter(Boolean).map((line) => JSON.parse(line));
  const generated = chunks.map((chunk) => chunk.response ?? '').join('');
  if (!generated.trim()) throw new Error('Ollama devolvió una traducción vacía.');
  return cleanModelOutput(generated);
}

function markdownSegmentsPrompt(sourcePath, segments, retryGuidance = '') {
  return `You are the senior bilingual editor of a professional LLM Engineering curriculum. Translate every supplied Markdown segment from Spanish to natural, precise technical English.

NON-NEGOTIABLE RULES:
- Return valid JSON only, with this exact shape: {"translations":[{"id":0,"text":"..."}]}.
- Return one item for every input item, with the same numeric id and no extra items.
- Translate every Spanish word in every text field; never stop partway through a segment.
- Preserve every Markdown element, heading level, list, table row, blockquote, checkbox, footnote, and line structure inside each text field.
- Placeholders shaped like ⟦LLMEC-A⟧ are immutable. Preserve every occurrence, count, and order exactly; never expand or format them.
- Do not translate product names, model IDs, API field names, identifiers, commands, paths, filenames, mathematical notation, or acronyms.
- Preserve factual meaning, cautions, dates, numbers, answer choices, answer keys, and pedagogical difficulty exactly.
- Use idiomatic professional English, not literal machine-translation phrasing. Use "you" for learner instructions.
- Do not add facts, promises, examples, solutions, or marketing language.
- This content is current as of 2026-08-21. Do not replace current model names with older ones.
${retryGuidance}

SOURCE PATH: ${sourcePath}

SEGMENTS:
${JSON.stringify(segments)}`;
}

function markdownBatches(segments, maxCharacters = 8_000, maxItems = 12) {
  const batches = [];
  let batch = [];
  let size = 0;
  for (const segment of segments) {
    if (batch.length && (size + segment.text.length > maxCharacters || batch.length >= maxItems)) {
      batches.push(batch);
      batch = [];
      size = 0;
    }
    batch.push(segment);
    size += segment.text.length;
  }
  if (batch.length) batches.push(batch);
  return batches;
}

function validateProtectedMarkers(source, translation) {
  for (const code of ['A', 'B', 'C', 'D', 'E', 'F']) {
    const token = `⟦LLMEC-${code}⟧`;
    const expected = source.split(token).length - 1;
    const actual = translation.split(token).length - 1;
    if (expected !== actual) throw new Error(`Marcador alterado en segmento: ${token} aparece ${actual}/${expected} veces.`);
  }
}

function restoreMarkdownPrefixes(source, translation, pattern) {
  const expected = [...source.matchAll(pattern)].map((match) => match[0]);
  const actual = [...translation.matchAll(pattern)];
  if (expected.length !== actual.length) return translation;
  let index = 0;
  return translation.replace(pattern, () => expected[index++]);
}

function normalizeMarkdownStructure(source, translation) {
  let normalized = translation;
  const sourceLines = source.split('\n');
  const translatedLines = normalized.split('\n');
  if (sourceLines.length === translatedLines.length) {
    const prefixPatterns = [/^#{1,6}[ \t]+/, /^([ \t]*)([-*+]|\d+[.)])[ \t]+/, /^[ \t]*>[ \t]?/];
    for (let lineIndex = 0; lineIndex < sourceLines.length; lineIndex += 1) {
      for (const pattern of prefixPatterns) {
        const sourcePrefix = sourceLines[lineIndex].match(pattern)?.[0] ?? '';
        const translatedPrefix = translatedLines[lineIndex].match(pattern)?.[0] ?? '';
        if (sourcePrefix || translatedPrefix) {
          translatedLines[lineIndex] = `${sourcePrefix}${translatedLines[lineIndex].slice(translatedPrefix.length)}`;
        }
      }
    }
    normalized = translatedLines.join('\n');
  }
  normalized = restoreMarkdownPrefixes(source, normalized, /^#{1,6}[ \t]+/gm);
  normalized = restoreMarkdownPrefixes(source, normalized, /^([ \t]*)([-*+]|\d+[.)])[ \t]+/gm);
  normalized = restoreMarkdownPrefixes(source, normalized, /^[ \t]*>[ \t]?/gm);
  return normalized;
}

async function translateMarkdown(sourcePath, source, seedOffset = 0) {
  const protectedMarkdown = protectMarkdown(source);
  const pieces = protectedMarkdown.source.split(/(\n{2,})/);
  const segments = pieces
    .map((text, pieceIndex) => ({ id: pieceIndex, pieceIndex, text }))
    .filter((segment) => segment.pieceIndex % 2 === 0 && segment.text.trim());
  const translatedByPiece = new Map();
  const batches = markdownBatches(segments);

  async function translateBatch(batch, batchIndex, depth = 0) {
    let lastError = null;
    let splitImmediately = false;
    for (let attempt = 0; attempt < 3; attempt += 1) {
      try {
        const raw = await generate(
          markdownSegmentsPrompt(
            sourcePath,
            batch.map(({ id, text }) => ({ id, text })),
            attempt ? `RETRY ${attempt + 1}: the previous output was invalid or left Spanish prose untranslated. Return every requested id exactly once.` : '',
          ),
          true,
          seedOffset + batchIndex * 101 + depth * 17 + attempt,
        );
        let payload;
        try { payload = JSON.parse(raw); }
        catch { throw new Error(`${sourcePath}: Ollama no devolvió JSON válido para Markdown.`); }
        const translations = payload?.translations;
        const byId = new Map(Array.isArray(translations) ? translations.map((item) => [item.id, item.text]) : []);
        if (translations?.length !== batch.length || batch.some((segment) => typeof byId.get(segment.id) !== 'string')) {
          splitImmediately = true;
          throw new Error(`${sourcePath}: lote Markdown incompleto (${translations?.length ?? 0}/${batch.length}).`);
        }
        for (const segment of batch) {
          const translatedSegment = byId.get(segment.id).replace(/\n{2,}/g, '\n');
          validateProtectedMarkers(segment.text, translatedSegment);
          byId.set(segment.id, normalizeMarkdownStructure(segment.text, translatedSegment));
        }
        const partial = batch.filter((segment) => englishQualityProblem(byId.get(segment.id)));
        if (partial.length) throw new Error(`${sourcePath}: el lote conserva español en los segmentos ${partial.map((segment) => segment.id).join(', ')}.`);
        for (const segment of batch) translatedByPiece.set(segment.pieceIndex, byId.get(segment.id));
        return;
      } catch (error) {
        lastError = error;
        if (splitImmediately) break;
      }
    }

    if (batch.length > 1) {
      const middle = Math.ceil(batch.length / 2);
      console.warn(`  · dividiendo lote incompleto ${batch.length} → ${middle}+${batch.length - middle}`);
      await translateBatch(batch.slice(0, middle), batchIndex, depth + 1);
      await translateBatch(batch.slice(middle), batchIndex, depth + 1);
      return;
    }
    throw lastError;
  }

  for (const [batchIndex, batch] of batches.entries()) {
    console.log(`  · lote Markdown ${batchIndex + 1}/${batches.length}`);
    await translateBatch(batch, batchIndex);
  }

  const assembled = pieces.map((piece, pieceIndex) => translatedByPiece.get(pieceIndex) ?? piece).join('');
  return normalizeMarkdownStructure(source, protectedMarkdown.restore(assembled));
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

function markdownArtifacts(source) {
  const fences = source.match(/^```[^\n]*\n[\s\S]*?^```[ \t]*$/gm) ?? [];
  const prose = source.replace(/^```[^\n]*\n[\s\S]*?^```[ \t]*$/gm, 'LLMEC_FENCE');
  return {
    fences: fences.map(fenceArtifact),
    headings: prose.match(/^#{1,6}\s+/gm) ?? [],
    strongMarkers: (prose.match(/\*\*/g) ?? []).length,
    inline: prose.match(/(?<!`)(`+)(?!`)([^\n]*?)\1(?!`)/g) ?? [],
    links: [...prose.matchAll(/\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g)].map((match) => match[1]),
    lists: [...prose.matchAll(/^([ \t]*)([-*+]|\d+[.)])[ \t]+/gm)].map((match) => `${match[1].length}:${match[2]}`),
    blockquotes: prose.match(/^[ \t]*>[ \t]?/gm) ?? [],
    tablePipes: prose.split('\n').filter((line) => (line.match(/\|/g) ?? []).length >= 2).map((line) => (line.match(/\|/g) ?? []).length),
    blankRuns: prose.match(/\n{2,}/g)?.map((run) => run.length) ?? [],
  };
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

function validateMarkdownIntegrity(sourcePath, source, translation) {
  const before = markdownArtifacts(source);
  const after = markdownArtifacts(translation);
  const changed = Object.keys(before).filter((key) => JSON.stringify(before[key]) !== JSON.stringify(after[key]));
  if (changed.length) throw new Error(`${sourcePath}: cambió estructura Markdown (${changed.join(', ')}).`);
}

function pythonSegmentsPrompt(sourcePath, segments) {
  return `Translate the human-facing docstrings and comments extracted from a Python training lab from Spanish to precise professional English.

NON-NEGOTIABLE RULES:
- Return valid JSON only, with this exact shape: {"translations":[{"id":0,"text":"..."}]}.
- Return one item for every input item, with the same numeric id and no extra items.
- Translate only the text field. Do not translate or alter code fragments, identifiers, formatting fields, URLs, commands, model IDs, environment variables, or numeric values found inside it.
- Preserve newlines where they carry structure. Do not add a solution or alter technical meaning.
- Keep all pedagogical warnings and instructions. Do not add a solution or alter behavior.

SOURCE PATH: ${sourcePath}

SEGMENTS:
${JSON.stringify(segments)}`;
}

function extractPythonSegments(sourceFile) {
  const program = String.raw`import ast, io, json, tokenize, sys
p=sys.argv[1]
s=open(p, encoding='utf-8').read()
tree=ast.parse(s, filename=p)
doc_starts=set()
for node in ast.walk(tree):
    body=getattr(node, 'body', None)
    if isinstance(body, list) and body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
        doc_starts.add((body[0].lineno, body[0].col_offset))
out=[]
for token in tokenize.generate_tokens(io.StringIO(s).readline):
    kind=tokenize.tok_name[token.type]
    if kind == 'COMMENT' and not token.string.startswith('#!') and 'coding:' not in token.string:
        raw=token.string
        prefix='# ' if raw.startswith('# ') else '#'
        out.append({'kind':'comment','start':token.start,'end':token.end,'prefix':prefix,'text':raw[len(prefix):]})
    elif kind == 'STRING' and token.start in doc_starts:
        raw=token.string
        import re
        match=re.match(r"(?is)^([rubf]*)(\"\"\"|'''|\"|')([\s\S]*)(\2)$", raw)
        if match:
            out.append({'kind':'docstring','start':token.start,'end':token.end,'prefix':match.group(1)+match.group(2),'suffix':match.group(2),'text':match.group(3)})
print(json.dumps(out, ensure_ascii=False))`;
  return JSON.parse(execFileSync('python3', ['-c', program, sourceFile], { encoding: 'utf8', maxBuffer: 8 * 1024 * 1024 }));
}

function offsetAt(source, line, column) {
  let offset = 0;
  for (let current = 1; current < line; current += 1) offset = source.indexOf('\n', offset) + 1;
  return offset + column;
}

async function translatePython(sourcePath, sourceFile, source, attempt = 0) {
  const segments = extractPythonSegments(sourceFile).map((segment, id) => ({ ...segment, id }));
  if (!segments.length) return source;
  const raw = await generate(
    pythonSegmentsPrompt(sourcePath, segments.map(({ id, kind, text }) => ({ id, kind, text }))),
    true,
    attempt,
  );
  let payload;
  try { payload = JSON.parse(raw); }
  catch { throw new Error(`${sourcePath}: Ollama no devolvió JSON válido para Python.`); }
  if (!Array.isArray(payload.translations) || payload.translations.length !== segments.length) {
    throw new Error(`${sourcePath}: se esperaban ${segments.length} segmentos y llegaron ${payload.translations?.length ?? 0}.`);
  }
  const byId = new Map(payload.translations.map((item) => [item.id, item.text]));
  let translated = source;
  for (const segment of [...segments].reverse()) {
    let value = byId.get(segment.id);
    if (typeof value !== 'string') throw new Error(`${sourcePath}: falta el segmento ${segment.id}.`);
    if (segment.kind === 'docstring') {
      if (segment.text.startsWith('\n') && !value.startsWith('\n')) value = `\n${value}`;
      if (segment.text.endsWith('\n') && !value.endsWith('\n')) value = `${value}\n`;
      if (value.includes(segment.suffix)) throw new Error(`${sourcePath}: comillas incompatibles en el docstring ${segment.id}.`);
    }
    const replacement = segment.kind === 'comment'
      ? `${segment.prefix}${value}`
      : `${segment.prefix}${value}${segment.suffix}`;
    const start = offsetAt(source, segment.start[0], segment.start[1]);
    const end = offsetAt(source, segment.end[0], segment.end[1]);
    translated = `${translated.slice(0, start)}${replacement}${translated.slice(end)}`;
  }
  return translated;
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

async function validatePython(sourcePath, sourceFile, translated) {
  const target = path.join(outputRoot, sourcePath);
  const temporary = `${target}.tmp`;
  const checked = `${temporary}.checked`;
  await mkdir(path.dirname(target), { recursive: true });
  await writeFile(temporary, translated);
  try {
    const before = pythonAstWithoutDocstrings(sourceFile);
    const after = pythonAstWithoutDocstrings(temporary);
    if (before !== after) throw new Error('La traducción cambió el AST fuera de docstrings.');
    await rm(checked, { force: true });
    await rename(temporary, checked);
  } catch (error) {
    await rm(temporary, { force: true });
    throw error;
  }
  return checked;
}

async function loadManifest() {
  try { return JSON.parse(await readFile(manifestPath, 'utf8')); }
  catch { return { version: 1, model, generatedAt: null, files: {} }; }
}

async function saveManifest(manifest) {
  manifest.generatedAt = new Date().toISOString();
  manifest.model = model;
  await mkdir(outputRoot, { recursive: true });
  const temporary = `${manifestPath}.${process.pid}.tmp`;
  await writeFile(temporary, `${JSON.stringify(manifest, null, 2)}\n`);
  await rename(temporary, manifestPath);
}

async function acquireManifestLock() {
  await mkdir(outputRoot, { recursive: true });
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

async function recordTranslation(sourcePath, record) {
  const release = await acquireManifestLock();
  try {
    const current = await loadManifest();
    current.files[sourcePath] = record;
    await saveManifest(current);
  } finally {
    await release();
  }
}

let paths = (await walk(root)).filter(isPublishable).sort();
if (selectedPath) paths = paths.filter((candidate) => candidate === selectedPath);
if (shardValue) {
  const match = shardValue.match(/^(\d+)\/(\d+)$/);
  if (!match) throw new Error('Usa --shard con formato índice/total, por ejemplo 0/2.');
  const shardIndex = Number(match[1]);
  const shardCount = Number(match[2]);
  if (!Number.isInteger(shardIndex) || !Number.isInteger(shardCount) || shardCount < 1 || shardIndex < 0 || shardIndex >= shardCount) {
    throw new Error(`Partición inválida: ${shardValue}.`);
  }
  paths = paths.filter((_candidate, index) => index % shardCount === shardIndex);
}
if (limit > 0) paths = paths.slice(0, limit);
if (!paths.length) throw new Error(selectedPath ? `No existe una fuente publicable: ${selectedPath}` : 'No se encontraron fuentes publicables.');

let translatedCount = 0;
let skippedCount = 0;

for (const [index, sourcePath] of paths.entries()) {
  const sourceFile = path.join(root, sourcePath);
  const target = path.join(outputRoot, sourcePath);
  const source = await readFile(sourceFile, 'utf8');
  const sourceHash = sha256(source);
  const known = (await loadManifest()).files[sourcePath];
  const pipelineVersion = sourcePath.endsWith('.md') ? 2 : 1;
  const currentPipeline = known?.pipelineVersion === pipelineVersion
    || (pipelineVersion === 1 && known?.pipelineVersion == null);
  let targetExists = false;
  try { targetExists = (await stat(target)).isFile(); } catch {}
  if (!force && targetExists && known?.sourceHash === sourceHash && currentPipeline) {
    skippedCount += 1;
    console.log(`[${index + 1}/${paths.length}] sin cambios ${sourcePath}`);
    continue;
  }

  console.log(`[${index + 1}/${paths.length}] traduciendo ${sourcePath}`);
  let translated;
  let translatedSuccessfully = false;
  for (let attempt = 0; attempt < 3 && !translatedSuccessfully; attempt += 1) {
    try {
      if (sourcePath.endsWith('.md')) {
        translated = await translateMarkdown(sourcePath, source, attempt);
        validateMarkdownIntegrity(sourcePath, source, translated);
        const qualityProblem = englishQualityProblem(translated);
        if (qualityProblem) throw new Error(`${sourcePath}: traducción inglesa parcial (${qualityProblem}).`);
        await mkdir(path.dirname(target), { recursive: true });
        await writeFile(target, translated);
      } else {
        translated = await translatePython(sourcePath, sourceFile, source, attempt);
        const checked = await validatePython(sourcePath, sourceFile, translated);
        await rename(checked, target);
      }
      translatedSuccessfully = true;
    } catch (error) {
      await rm(`${target}.tmp`, { force: true });
      await rm(`${target}.tmp.checked`, { force: true });
      if (attempt === 2) throw error;
      console.warn(`[${index + 1}/${paths.length}] reintento ${attempt + 2}/3 ${sourcePath}: ${error.message}`);
    }
  }

  await recordTranslation(sourcePath, {
    sourceHash,
    translationHash: sha256(translated),
    model,
    pipelineVersion,
    translatedAt: new Date().toISOString(),
  });
  translatedCount += 1;
}

console.log(`Traducción terminada: ${translatedCount} nuevas, ${skippedCount} sin cambios.`);
