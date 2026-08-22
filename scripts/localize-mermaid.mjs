import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdir, readFile, readdir, rm, stat, writeFile } from 'node:fs/promises';
import path from 'node:path';

const root = process.cwd();
const translationRoot = path.join(root, 'translations', 'en');
const manifestPath = path.join(translationRoot, '.translation-manifest.json');
const manifestLockPath = path.join(translationRoot, '.translation-manifest.lock');
const sha256 = (value) => createHash('sha256').update(value).digest('hex');

const replacements = [
  ['revisión humana', 'human review'], ['Revisión humana', 'Human review'],
  ['evidencia de evaluación', 'evaluation evidence'], ['Evidencia de evaluación', 'Evaluation evidence'],
  ['pregunta del usuario', 'user question'], ['Pregunta del usuario', 'User question'],
  ['respuesta final', 'final answer'], ['Respuesta final', 'Final answer'],
  ['resultado final', 'final result'], ['Resultado final', 'Final result'],
  ['búsqueda web', 'web search'], ['Búsqueda web', 'Web search'],
  ['búsqueda por similitud', 'similarity search'], ['Búsqueda por similitud', 'Similarity search'],
  ['construcción del prompt', 'prompt construction'], ['Construcción del prompt', 'Prompt construction'],
  ['fase de indexado', 'indexing phase'], ['Fase de indexado', 'Indexing phase'],
  ['fase de consulta', 'query phase'], ['Fase de consulta', 'Query phase'],
  ['modelo bi-encoder', 'bi-encoder model'], ['mismo modelo', 'same model'],
  ['vectores + metadatos + texto', 'vectors + metadata + text'],
  ['fuentes: PDFs, Markdown', 'sources: PDFs, Markdown'], ['Fuentes: PDFs, Markdown', 'Sources: PDFs, Markdown'],
  ['extracción y limpieza', 'extraction and cleaning'], ['Extracción y limpieza', 'Extraction and cleaning'],
  ['contexto + pregunta', 'context + question'], ['system + contexto', 'system + context'],
  ['con citas', 'with citations'], ['genera respuesta', 'generates an answer'],
  ['similitud entre consecutivas', 'similarity between adjacent sentences'], ['Similitud entre consecutivas', 'Similarity between adjacent sentences'],
  ['¿Caída bajo umbral?', 'Drop below threshold?'], ['frontera de chunk', 'chunk boundary'], ['Frontera de chunk', 'Chunk boundary'],
  ['misma unidad temática', 'same topic unit'], ['Misma unidad temática', 'Same topic unit'],
  ['se entrega al LLM', 'sent to the LLM'], ['match con', 'match with'],
  ['millones de docs', 'millions of docs'], ['reordenado', 'reranked'], ['Contexto del LLM', 'LLM context'],
  ['query original', 'original query'], ['Query original', 'Original query'], ['reformulaciones', 'rewrites'],
  ['búsqueda 1', 'search 1'], ['búsqueda 2', 'search 2'], ['búsqueda 3', 'search 3'], ['Fusión RRF', 'RRF fusion'], ['top-k final', 'final top-k'],
  ['evaluador de', 'evaluator of'], ['Evaluador de', 'Evaluator of'], ['relevancia', 'relevance'],
  ['refinar: filtrar', 'refine: filter'], ['Refinar: filtrar', 'Refine: filter'], ['las tiras relevantes', 'relevant passages'],
  ['refinar + búsqueda web', 'refine + web search'], ['Refinar + búsqueda web', 'Refine + web search'],
  ['descartar corpus', 'discard corpus'], ['Descartar corpus', 'Discard corpus'], ['Generar', 'Generate'],
  ['ingesta gestionada', 'managed ingestion'], ['Ingesta gestionada', 'Managed ingestion'], ['S3 u otros', 'S3 or other'],
  ['data sources', 'data sources'], ['Tu aplicación', 'Your application'], ['recuperación + LLM', 'retrieval + LLM'], ['Retrieval + LLM', 'Retrieval + LLM'],
  ['qué evalúa cada métrica', 'what each metric evaluates'], ['Qué evalúa cada métrica', 'What each metric evaluates'],
  ['evalúa retrieval', 'evaluates retrieval'], ['Evalúa retrieval', 'Evaluates retrieval'], ['evalúa generación', 'evaluates generation'], ['Evalúa generación', 'Evaluates generation'],
  ['necesita ground truth', 'needs ground truth'], ['Necesita ground truth', 'Needs ground truth'], ['no necesita ground truth', 'does not need ground truth'], ['No necesita ground truth', 'Does not need ground truth'],
  ['cambio en el pipeline', 'pipeline change'], ['Cambio en el pipeline', 'Pipeline change'], ['eval barata', 'low-cost eval'], ['Eval barata', 'Low-cost eval'],
  ['sobre dataset versionado', 'on a versioned dataset'], ['monitorización en prod', 'production monitoring'], ['Monitorización en prod', 'Production monitoring'],
  ['muestreo + feedback usuarios', 'sampling + user feedback'], ['nuevos fallos', 'new failures'], ['Añadir casos al dataset', 'Add cases to the dataset'], ['añadir casos al dataset', 'add cases to the dataset'],
  ['estado, ciclos, checkpoints', 'state, cycles, checkpoints'], ['supervisor y comunicación', 'supervisor and communication'],
  ['trabajo, episódica, semántica', 'working, episodic, semantic'], ['herramientas estandarizadas entre apps', 'standardized tools across apps'],
  ['trayectorias, coste, guardrails', 'trajectories, cost, guardrails'], ['versión gestionada en AWS', 'managed version on AWS'],
  ['equivalente cloud', 'cloud equivalent'], ['por qué los modelos', 'why models'], ['obedecen herramientas', 'follow tool calls'],
  ['acción + argumentos', 'action + arguments'], ['observación', 'observation'], ['tarea del usuario', 'user task'], ['Tarea del usuario', 'User task'],
  ['llamada al LLM', 'LLM call'], ['Llamada al LLM', 'LLM call'], ['¿tool_calls?', 'tool_calls?'], ['ejecutar herramienta', 'execute tool'], ['Ejecutar herramienta', 'Execute tool'],
  ['añadir observación', 'add observation'], ['Añadir observación', 'Add observation'], ['como mensaje tool', 'as a tool message'],
  ['¿iteraciones < MAX?', 'iterations < MAX?'], ['cortar: informar', 'stop: report'], ['Cortar: informar', 'Stop: report'], ['de límite alcanzado', 'iteration limit reached'],
  ['plan = pasos 1..n', 'plan = steps 1..n'], ['paso i', 'step i'], ['¿plan válido?', 'valid plan?'], ['sí, siguiente paso', 'yes, next step'],
  ['ajustar', 'adjust'], ['completado', 'complete'], ['Intento k', 'Attempt k'], ['Intento k+1', 'Attempt k+1'],
  ['tests / juez', 'tests / judge'], ['éxito', 'success'], ['fracaso', 'failure'], ['reflexión verbal', 'verbal reflection'], ['Reflexión verbal', 'Verbal reflection'],
  ['por qué fallé, qué cambiar', 'why I failed, what to change'], ['Memoria episódica', 'Episodic memory'], ['con reflexiones en contexto', 'with reflections in context'], ['Fin', 'Done'],
  ['el último mensaje', 'the latest message'], ['tiene tool_calls?', 'has tool_calls?'], ['Humano', 'Human'], ['Grafo', 'Graph'],
  ['checkpoint tras nodo agent', 'checkpoint after agent node'], ['propone: borrar_registros', 'proposes: delete_records'], ['pausado — ¿aprobar?', 'paused — approve?'],
  ['aprueba', 'approves'], ['checkpoint tras tools', 'checkpoint after tools'], ['resultado final', 'final result'], ['Resultado final', 'Final result'],
  ['tu app', 'your app'], ['Modelo', 'Model'], ['proceso local', 'local process'], ['remoto', 'remote'], ['Ficheros', 'Files'],
  ['Usuario', 'User'], ['|"delega"|', '|"delegates"|'], ['búsqueda', 'search'], ['cálculo', 'calculation'], ['sin tools', 'no tools'], ['resultado', 'result'],
  ['¿El flujo es fijo?', 'Is the flow fixed?'], ['no es multi-agente', 'not multi-agent'], ['¿Un agente con buenas tools', 'Can one agent with good tools'], ['resuelve con calidad?', 'solve it well?'],
  ['Un solo agente', 'One agent'], ['la opción por defecto', 'the default choice'], ['no: demasiadas tools', 'no: too many tools'], ['contexto o especialización', 'context or specialization'],
  ['¿El dominio es', 'Is the domain'], ['enrutar conversaciones?', 'conversation routing?'], ['subagentes aislados', 'isolated subagents'], ['Jerárquico', 'Hierarchical'],
  ['Aplicación', 'Application'], ['Lambda o retorno de control', 'Lambda or return of control'], ['sistema interno', 'internal system'], ['evaluación', 'evaluation'],
  ['duración total', 'total duration'], ['coste', 'cost'], ['trazas + evals', 'traces + evals'], ['métricas', 'metrics'], ['muestreo de tráfico', 'traffic sampling'],
  ['Dataset de evaluación', 'Evaluation dataset'], ['casos + expectativas', 'cases + expectations'], ['ejecuta el sistema', 'runs the system'], ['sobre cada caso', 'on each case'],
  ['Evaluadores', 'Evaluators'], ['código + LLM-as-judge', 'code + LLM-as-judge'], ['Agregación', 'Aggregation'], ['scores por caso y por suite', 'scores by case and suite'],
  ['¿Umbral', 'Threshold'], ['superado?', 'passed?'], ['CI verde', 'Green CI'], ['CI rojo', 'Red CI'], ['informe', 'report'],
  ['¿Vecino en cache con', 'Cached neighbor with'], ['similitud ≥ umbral?', 'similarity ≥ threshold?'], ['Devolver respuesta cacheada', 'Return cached answer'],
  ['Llamada LLM', 'LLM call'], ['coste completo', 'full cost'], ['Guardar (embedding, respuesta)', 'Store (embedding, answer)'], ['en la cache', 'in the cache'],
  ['solo el venv', 'only the venv'], ['nada de toolchain', 'no toolchain'], ['Cliente', 'Client'], ['ALB o API Gateway', 'ALB or API Gateway'],
  ['ECS Fargate o Lambda', 'ECS Fargate or Lambda'], ['Job de ingestión', 'Ingestion job'], ['logs/métricas/trazas', 'logs/metrics/traces'],
  ['Usuario objetivo', 'Target user'], ['Tu sistema', 'Your system'], ['Proveedor LLM', 'LLM provider'], ['APIs externas de las herramientas', 'External tool APIs'],
  ['Plataforma: nómbrala', 'Platform: name it'], ['Grafo del agente', 'Agent graph'], ['Servicio de retrieval', 'Retrieval service'],
  ['Vector DB: nómbrala', 'Vector DB: name it'], ['Herramienta 2', 'Tool 2'], ['Herramienta 3', 'Tool 3'], ['Pipeline de ingestión', 'Ingestion pipeline'], ['job offline', 'offline job'],
  ['Agente', 'Agent'], ['pregunta', 'question'], ['invoca grafo', 'invokes graph'], ['decide herramienta', 'selects tool'], ['chunks + metadatos', 'chunks + metadata'],
  ['genera respuesta', 'generates answer'], ['respuesta + citas', 'answer + citations'], ['query del usuario', 'user query'], ['resultado o error descriptivo', 'result or descriptive error'],
  ['la herramienta tiene efectos', 'the tool has side effects'], ['usuario aprueba', 'user approves'], ['usuario rechaza', 'user rejects'], ['criterio de parada', 'stopping criterion'],
  ['presupuesto agotado', 'budget exhausted'], ['salida digna', 'graceful exit'], ['Confirmacion', 'Confirmation'], ['Herramienta', 'Tool'], ['Respuesta', 'Answer'],
  ['timeouts largos', 'long timeouts'], ['Réplica vLLM', 'vLLM replica'], ['modelo evaluado y fijado', 'evaluated, pinned model'],
  ['volumen de pesos', 'weights volume'], ['los modelos NO van en la imagen', 'models are NOT stored in the image'], ['uso de KV cache, colas', 'KV-cache use, queues'],
  ['Tu API FastAPI', 'Your FastAPI API'], ['la del capítulo 04', 'from chapter 04'], ['cliente OpenAI', 'OpenAI client'], ['base_url interna', 'internal base_url'],
  ['Herramienta externa', 'External tool'], ['cloud pública', 'public cloud'], ['Ingestión', 'Ingestion'], ['trazas', 'traces'], ['métricas', 'metrics'],
  ['latencia', 'latency'], ['alertas', 'alerts'], ['Documento', 'Document'], ['Ingesta', 'Ingestion'], ['Evaluación', 'Evaluation'], ['Resultado', 'Result'],
  ['llamada LLM', 'LLM call'], ['tarea', 'task'],
  ['posición', 'position'], ['capas', 'layers'], ['representaciones', 'representations'], ['sobre vocabulario', 'over vocabulary'],
  ['Hipótesis', 'Hypothesis'], ['Diff de prompt', 'Prompt diff'], ['Eval offline', 'Offline eval'], ['gate verde', 'green gate'], ['Shadow o canary', 'Shadow or canary'],
  ['regresión', 'regression'], ['Métricas online', 'Online metrics'], ['cumple', 'passes'], ['Promoción', 'Promotion'], ['degrada', 'degrades'], ['Rollback por versión', 'Version rollback'],
  ['interfaz', 'interface'], ['índice versionado', 'versioned index'], ['Generador grounded', 'Grounded generator'], ['trazas y feedback', 'traces and feedback'],
  ['runner de evaluación', 'evaluation runner'], ['artefacto por caso', 'artifact per case'], ['Frases', 'Sentences'], ['Embeddings por frase', 'Embeddings per sentence'],
  ['Padre: sección', 'Parent: section'], ['hijo', 'child'], ['indexado', 'indexed'], ['Etapa', 'Stage'], ['Fusión', 'Fusion'],
  ['pasa', 'passes'], ['mejora', 'improves'], ['nuevos', 'new'], ['sí', 'yes'], ['no', 'no'], ['Tarea', 'Task'],
];

const spanishSignal = /\b(?:usuario|tarea|pregunta|respuesta|resultado|herramienta|observación|búsqueda|evaluación|métricas|coste|trazas|ingesta|modelo|interfaz|índice|documento|frases|sección|hijo|padre|capas|posición|regresión|promoción|degrada|cumple|añadir|ejecutar|llamada|límite|paso|sí)\b/iu;

async function walk(directory) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.name.startsWith('.')) continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) files.push(...await walk(absolute));
    else if (entry.name.endsWith('.md')) files.push(absolute);
  }
  return files;
}

const staged = new Map();
const remaining = [];
for (const file of await walk(translationRoot)) {
  const original = await readFile(file, 'utf8');
  const localized = original.replace(/^```mermaid\n([\s\S]*?)^```[ \t]*$/gm, (block) => {
    let result = block;
    for (const [spanish, english] of replacements.sort((left, right) => right[0].length - left[0].length)) result = result.split(spanish).join(english);
    if (spanishSignal.test(result)) remaining.push(`${path.relative(translationRoot, file)}: ${result.split('\n').find((line) => spanishSignal.test(line))?.trim()}`);
    return result;
  });
  if (localized !== original) staged.set(file, localized);
}

if (remaining.length) {
  console.error(`Quedan etiquetas Mermaid en español (${remaining.length}):\n- ${remaining.join('\n- ')}`);
  process.exit(1);
}
if (staged.size) console.log(`Diagramas actualizados: ${[...staged.keys()].map((file) => path.relative(translationRoot, file)).join(', ')}`);

async function acquireLock() {
  for (let attempt = 0; attempt < 1200; attempt += 1) {
    try {
      await mkdir(manifestLockPath);
      return async () => rm(manifestLockPath, { recursive: true, force: true });
    } catch (error) {
      if (error?.code !== 'EEXIST') throw error;
      const lock = await stat(manifestLockPath).catch(() => null);
      if (lock && Date.now() - lock.mtimeMs > 60_000) { await rm(manifestLockPath, { recursive: true, force: true }); continue; }
      await new Promise((resolve) => setTimeout(resolve, 50));
    }
  }
  throw new Error('Timeout esperando el manifiesto de traducción.');
}

const release = await acquireLock();
try {
  const manifest = JSON.parse(await readFile(manifestPath, 'utf8'));
  const reviewedAt = new Date().toISOString();
  for (const [file, localized] of staged) {
    await writeFile(file, localized);
    const sourcePath = path.relative(translationRoot, file).split(path.sep).join('/');
    const source = await readFile(path.join(root, sourcePath), 'utf8');
    manifest.files[sourcePath] = {
      ...manifest.files[sourcePath],
      sourceHash: sha256(source),
      translationHash: sha256(localized),
      model: 'human-reviewed',
      editor: process.env.GITHUB_ACTOR || process.env.USER || null,
      pipelineVersion: 2,
      reviewedAt,
    };
  }
  manifest.generatedAt = reviewedAt;
  await writeFile(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`);
} finally {
  await release();
}

execFileSync(process.execPath, ['scripts/validate-translations.mjs'], { cwd: root, stdio: 'inherit' });
console.log(`Diagramas Mermaid localizados en ${staged.size} documentos.`);
