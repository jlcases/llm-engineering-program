# Panorámica actual: GPT-5.6, Claude 5, Gemini 3.x, Llama 4 y Mistral

> **Módulo 1 · Tema 4** · Tiempo estimado de estudio: 2 h
> Labs asociados: `labs/01_primer_llamada_openai.py`, `labs/02_primer_llamada_anthropic.py`
> Ejercicios asociados: 5, 6, 7 y 10.

> ⚠️ **Caducidad.** Este es el tema del módulo que más rápido envejece. Los nombres y
> capacidades concretas descritas aquí son una foto del **21 de agosto de 2026**; lo que debe
> quedarte no es la foto, sino el **mapa de familias** y el **método para evaluar**
> cualquier modelo nuevo que aparezca (sección 6).

---

## 1. Cómo leer el mercado: los tres ejes

Para no perderte entre decenas de nombres, sitúa cada modelo en tres ejes:

1. **Acceso**: ¿pesos cerrados tras una API (GPT, Claude, Gemini) o pesos abiertos que
   puedes descargar y servir tú (Llama, Mistral, Qwen, DeepSeek)? "Open weights" no
   siempre es open source: lee la licencia (la de Llama tiene cláusulas comerciales;
   Mistral publica algunos modelos en Apache 2.0).
2. **Tamaño/tier**: cada proveedor mantiene una escalera — un modelo insignia (caro,
   máxima capacidad), uno intermedio y uno pequeño/barato para tareas de volumen.
   Aprenderse la escalera importa más que aprenderse los nombres: *la mayoría de las
   tareas de producción van bien con el tier pequeño o medio*.
3. **Régimen de inferencia**: modelos "clásicos" (responden directamente) vs modelos de
   **razonamiento configurable** (GPT-5.6, thinking adaptativo de Claude, Gemini thinking
   y modelos abiertos de reasoning). No necesitas ni debes depender de la cadena privada:
   evalúa la respuesta, sus evidencias y el uso de herramientas. Más razonamiento puede
   mejorar matemáticas/código/planificación a cambio de latencia y coste.

---

## 2. Las familias propietarias

### OpenAI: GPT-5.6

- La familia vigente es **GPT-5.6**, con esfuerzo de razonamiento configurable y tres
  perfiles explícitos: **Luna** para volumen sensible a coste, **Terra** como equilibrio
  y **Sol** para máxima capacidad. Los labs usan `gpt-5.6-luna`; cada proyecto debe
  promover otro tier solo si su eval lo justifica.
- La API recomendada para integraciones nuevas es **Responses**: unifica salidas tipadas,
  tools y continuidad. Chat Completions sigue siendo útil al mantener sistemas legacy,
  pero no es el punto de partida del curso.
- La generación 5.6 añade capacidades que cambian la arquitectura de agentes: **persisted
  reasoning** para continuar trabajo entre turnos, **Programmatic Tool Calling (PTC)** para
  orquestar herramientas desde código generado, modo de razonamiento `pro` para los casos
  más difíciles y `safety_identifier` para asociar abuso a un usuario sin enviar datos
  personales. No todas las tareas necesitan estas funciones: se activan cuando una eval
  demuestra que compensan su coste y latencia.
- GPT-4o y la o-series fueron pasos históricos importantes hacia multimodalidad y
  reasoning comercial. Se conservan en capítulos históricos y en nombres de encodings,
  no como defaults operativos.

### Anthropic: Claude

- El catálogo de agosto de 2026 ofrece **Claude Fable 5** como máxima capacidad para
  agentes de ejecución larga, **Claude Opus 5** para código agéntico complejo y trabajo
  empresarial, y **Claude Sonnet 5** como equilibrio; **Claude Haiku 4.5** sigue siendo
  el tier rápido vigente.
- En Claude 5 el control moderno es **adaptive thinking**: el modelo decide dinámicamente
  cuánto razonar según el problema y el esfuerzo configurado. No lo confundas con el
  *extended thinking* manual de generaciones anteriores, que sigue disponible en Haiku
  4.5 pero no es el mecanismo de Sonnet 5. Comprueba siempre la matriz de compatibilidad
  del snapshot que vas a usar.
- Otras señas de identidad: contextos largos, código y uso de herramientas/agentes, y
  énfasis en seguridad/steerability. API propia (`messages`), también disponible vía
  Bedrock y Vertex.
- En los labs usamos `claude-haiku-4-5`. En producción fija el snapshot con fecha cuando
  esté disponible y corre la evaluación antes de migrarlo.

### Google: Gemini

- En agosto de 2026, **Gemini 3.7 Flash** es el workhorse estable recomendado y **Gemini
  3.6 Flash** la generación estable anterior. **Gemini 3.5 Flash** sigue disponible como
  legacy estable y **Gemini 3.5 Flash-Lite** cubre volumen sensible a coste; **Gemini 3.1
  Pro** aparece como preview. Esta distinción importa: un preview sirve para evaluar, no
  debe entrar en producción por inercia. Gemini 1.5/2.x fueron hitos históricos de
  contexto masivo, multimodalidad y thinking integrado.
- Fortalezas: contexto enorme, integración con el ecosistema Google (Workspace, Vertex
  AI), y tiers Flash muy competitivos en precio. Los modelos abiertos de Google se
  llaman **Gemma**.

---

## 3. Las familias abiertas

### Meta: Llama

- **Llama 4 Scout y Maverick** siguen siendo la línea descargable open-weight vigente de
  Meta en esta foto y movieron la familia a Mixture-of-Experts multimodal. Meta también
  ofrece **Muse Spark** en sus productos propios desde 2026, pero no es una nueva versión
  descargable de Llama: no lo presentes como sustituto on-premise. Llama 3.x permanece
  muy desplegada y es útil para entender la transición, pero no debe asumirse como la
  mejor opción nueva.
- Su importancia es de ecosistema: la mayor parte del tooling local (llama.cpp, Ollama,
  vLLM, fine-tuning barato) creció alrededor de Llama, y su licencia —aunque no es OSS
  pura— permitió a las empresas desplegar en su propia infraestructura.

### Mistral

- Startup europea (Francia). El catálogo general de agosto de 2026 se articula alrededor
  de **Mistral Medium 3.5**, **Mistral Small 4** y **Mistral Large 3**, además de modelos
  especializados de código, razonamiento, OCR y audio. Mistral 7B y Mixtral 8x7B son
  hitos históricos, no la recomendación automática para un despliegue nuevo.
- Relevante si te importa: soberanía europea del dato, despliegue on-premise, y modelos
  pequeños muy eficientes.

### El resto del pelotón abierto (no lo ignores)

**Qwen** (Alibaba) mantiene Qwen3 como generación abierta y una línea API 3.x que ya
incluye Qwen 3.6; **DeepSeek** (cuyo R1, enero 2025, demostró razonamiento de frontera
con pesos abiertos y coste de entrenamiento modesto) compite de tú a tú con Llama. Si
trabajas con modelos locales en 2026, lo más probable es que acabes probando Qwen o
DeepSeek antes que nada. Comprueba el snapshot y la licencia exactos: estos catálogos no
se actualizan al mismo ritmo que las generaciones cerradas.

---

## 4. Tabla-resumen (foto del 21 de agosto de 2026)

| Proveedor | Familia | Tiers típicos | Acceso | Rasgo diferencial |
|---|---|---|---|---|
| OpenAI | GPT-5.6 Luna / Terra / Sol | volumen ↔ insignia | API | Responses, tools y reasoning configurable |
| Anthropic | Claude Haiku 4.5 / Sonnet 5 / Opus 5 / Fable 5 | rápido ↔ agentes largos | API (+Bedrock/Vertex) | Código, agentes, contexto largo, thinking adaptativo |
| Google | Gemini 3.5–3.7 Flash / 3.1 Pro preview | Flash-Lite ↔ Pro | API (+Vertex) | Contexto largo y multimodalidad |
| Meta | Llama 4 | tamaños/MoE según variante | Pesos abiertos | Ecosistema local y despliegue propio |
| Mistral | Medium 3.5 / Small 4 / Large 3 | Small ↔ Large | Mixto | Eficiencia, despliegue y soberanía europea |
| Alibaba | Qwen 3.x | múltiples tamaños | Pesos abiertos/API | Multilingüe, código y gama amplia |
| DeepSeek | catálogo V/R vigente | según variante | Pesos abiertos/API | Reasoning y despliegue eficiente |

---

## 5. Criterios de elección en la práctica

Preguntas en orden, de más eliminatoria a menos:

1. **¿Restricciones de datos/despliegue?** Si los datos no pueden salir de tu infra →
   pesos abiertos (o API en tu cloud vía Bedrock/Vertex/Azure). Esto elimina la mitad de
   la tabla de un plumazo.
2. **¿Qué necesita la tarea?** Contexto (¿caben tus documentos?), modalidades (¿imagen?
   ¿audio?), idioma (rendimiento real en español), herramientas (function calling,
   structured output), ¿razonamiento profundo o velocidad?
3. **¿Qué latencia y coste tolera el producto?** Un chatbot de soporte con miles de
   conversaciones/día vive en el tier pequeño; un análisis jurídico puntual puede
   permitirse el insignia con razonamiento. Precios: siempre en la página oficial de
   pricing del proveedor (cambian varias veces al año; cualquier cifra escrita aquí
   estaría mal en meses).
4. **¿Qué dice TU eval?** La única respuesta definitiva (sección 6).

Patrón de arquitectura muy común: **enrutado por dificultad** — el tier barato atiende
el 90 % de las peticiones y escala al modelo grande solo los casos difíciles.

---

## 6. Cómo evaluar un modelo nuevo (el método que no caduca)

Cada pocos meses saldrá "el mejor modelo de la historia". Protocolo:

1. **Desconfía de los benchmarks clásicos.** MMLU, HumanEval y compañía están saturados
   y contaminados (sus datos acaban en los corpus de entrenamiento). Diferencias de 1-2
   puntos no significan nada.
2. **Mira comparativas vivas** con sus limitaciones: LMArena (preferencias humanas
   ciegas; mide "gustar", no "acertar"), leaderboards de código tipo SWE-bench, Artificial
   Analysis para la relación calidad/precio/latencia.
3. **Construye tu mini-eval.** 20-50 casos reales de *tu* aplicación con criterio de
   corrección definido. Córrelo contra el modelo nuevo y el actual. Media hora de trabajo
   que vale más que cualquier nota de prensa. (En el módulo de evaluación del programa
   se sistematiza esto; la regla ya la conoces del laboratorio de benchmarking: publicar
   solo desde el harness serio.)
4. **Mide lo no-funcional**: latencia p95, tasa de errores/refusals, estabilidad del
   formato de salida, coste real por petición con *tus* prompts (recuerda del tema 2:
   el recuento de tokens difiere entre tokenizadores).
5. **Fija versiones en producción.** `model="...-latest"` o alias flotantes = tu app
   cambia de comportamiento sin avisar. Usa snapshots con fecha y migra deliberadamente.

---

## 7. Errores comunes

1. **Elegir modelo por titulares o por un benchmark único.** La pregunta no es "¿cuál es
   el mejor?" sino "¿cuál es el más barato que supera mi listón de calidad?".
2. **Usar el insignia para todo.** Pagar mucho más por tareas que el tier pequeño resuelve
   igual de bien es el error de costes más común en producción.
3. **Ignorar los modelos de razonamiento… o abusar de ellos.** Para lógica compleja son
   otra liga; para extraer un campo de un email son latencia y dinero tirados.
4. **Asumir que "open weights" = gratis.** Servir un 70B con buena latencia cuesta GPU,
   ingeniería y operación; a bajo volumen, la API sale más barata casi siempre.
5. **No releer la licencia** de los modelos abiertos antes de un uso comercial.
6. **Tratar los alias `-latest` como versiones estables** en producción.
7. **Evaluar en inglés y desplegar en español** sin comprobar la degradación.

---

## 8. Para profundizar

- **Fichas y documentación oficiales de modelos**:
  OpenAI: https://developers.openai.com/api/docs/models ·
  Anthropic: https://platform.claude.com/docs/en/about-claude/models/overview ·
  Gemini: https://ai.google.dev/gemini-api/docs/models ·
  Llama/Meta: https://ai.meta.com/llama/get-started/ ·
  Qwen: https://qwenlm.github.io/qwen-code-docs/en/users/configuration/model-providers/ ·
  Mistral: https://docs.mistral.ai/models
- **LMArena (antes LMSYS Chatbot Arena)** — ranking por preferencia humana:
  https://lmarena.ai/
- **Artificial Analysis** — comparativas de calidad/precio/latencia entre APIs:
  https://artificialanalysis.ai/
- **SWE-bench** — evaluación de código sobre issues reales de GitHub:
  https://www.swebench.com/
- **DeepSeek-R1 (2025)** — paper del razonamiento con RL en abierto:
  https://arxiv.org/abs/2501.12948
