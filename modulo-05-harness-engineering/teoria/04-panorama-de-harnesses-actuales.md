# 04 — Panorama actual: comparar arquitectura, no marcas

Un listado de funciones caduca; una lectura arquitectónica permite entender el siguiente producto
que aparezca. Esta unidad usa quince sistemas revisados el 23 de agosto de 2026 para aprender a
localizar quién posee el bucle, de dónde llega el contexto, dónde se aplica la autoridad y qué clase
de resultado puede atribuirse al harness.

La selección es un conjunto de referencia por diversidad arquitectónica, no un censo ni un ranking.
La ausencia de un producto no implica un juicio de calidad. El catálogo estructurado y sus fuentes
están en [`harness_landscape.json`](../labs/data/harness_landscape.json).

## 1. Cinco capas que suelen llamarse «harness»

| Capa | Qué posee | Pregunta de ingeniería | Ejemplos del catálogo |
|---|---|---|---|
| **Coding agent runtime** | Bucle, contexto de repo, tools y sesión de un agente | ¿Cómo convierte decisiones del modelo en cambios verificables? | dsh, OpenCode, Goose, Crush, Aider, Claude Code, Pi, Orca de echoVic |
| **Personal agent runtime** | Memoria persistente, skills, canales y subagentes | ¿Qué aprende entre sesiones y qué debe olvidar? | Hermes Agent, OpenHarness/Ohmo |
| **Integrated agent product** | Runtime más contexto de IDE, CLI y UX de aprobación | ¿Qué ventaja procede del editor y cuál del loop? | Kilo Code, Cline, Continue |
| **Multi-agent ADE** | Procesos, worktrees y supervisión de varios agentes | ¿Cómo aísla, compara y fusiona candidatos? | Orca de stablyai |
| **Workflow orchestrator** | Etapas deterministas que delegan turnos agénticos | ¿Qué control se expresa en código en vez de pedírselo al modelo? | Orca de VirtusLab |

La capa no es una nota. Un orquestador no es «más avanzado» que un runtime: resuelve otro problema.
Solo puedes atribuir una diferencia al mecanismo del harness cuando ambos candidatos ocupan la
misma capa, reciben la misma superficie y trabajan bajo contratos equivalentes.

## 2. Quince sistemas, quince preguntas útiles

| Sistema | Rasgo arquitectónico que importa | Experimento que merece la pena |
|---|---|---|
| **DeepSeek Harness (`dsh`)** | Adaptador, tools, log, sandbox y hasta el agent loop son plugins | Sustituir solo el loop y medir recuperación sin cambiar modelo ni autoridad |
| **OpenCode** | Runtime de coding con superficies terminal, escritorio, IDE y headless | Fijar una superficie y someter contexto y compaction a presión |
| **Goose** | Agente generalista extensible por MCP, no limitado al código | Comparar manifest mínimo y completo con el mismo modelo |
| **Crush** | TUI nativa con sesiones y endpoints compatibles | Separar overhead del proceso de calidad del loop |
| **Aider** | El modelo emite protocolos textuales de edición, no la misma mecánica de tool calling | Usarlo como baseline para modelos que fallan llamadas estructuradas |
| **Hermes Agent** | Memoria, skills y subagentes sobreviven a una tarea aislada | Medir transferencia legítima en un segundo pase sin filtrar la respuesta |
| **Claude Code** | Runtime de referencia con una superficie de capacidades exigente | Medir presión de schemas y recuperación, sin asumir compatibilidad no documentada |
| **Pi** | Runtime extensible con cuatro tools por defecto y sin permisos incorporados | Aislarlo externamente y barrer tamaño de la superficie de tools |
| **Orca — stablyai** | Coordina agentes existentes en worktrees paralelos | Medir best-of-N, coste duplicado, contaminación y carga de merge |
| **Orca — VirtusLab** | Flujos tipados, deterministas y reanudables por etapas | Asignar runtime/modelo por rol y medir el sistema compuesto |
| **Orca — echoVic** | Coding agent Rust de tercero con sesiones reanudables | Verificar si sus defaults específicos ayudan bajo un endpoint y sandbox fijados |
| **OpenHarness/Ohmo** | Infraestructura de tools, skills, memoria y coordinación más un agente de referencia | Separar el valor del framework del comportamiento de Ohmo |
| **Kilo Code** | Comparte producto entre VS Code, JetBrains y CLI | Comparar IDE y CLI controlando diagnósticos y contexto ambiente |
| **Cline** | Motor compartido por IDE, CLI y SDK con aprobación humana | Mantener el mismo régimen de aprobación en todos los trials |
| **Continue** | Combina flujos de agente con asistencia y autocompletado de editor | Evaluar cada workload por separado, nunca con una única puntuación |

Las últimas columnas del catálogo distinguen hechos verificados de hipótesis. «Tiene memoria» puede
ser un hecho de diseño. «La memoria mejora el resultado» sigue siendo una hipótesis hasta que un
experimento controle la contaminación, el primer pase y el segundo.

## 3. El caso Orca: mismo nombre, tres identidades

Tratar «Orca» como una sola herramienta destruye cualquier comparativa:

1. [stablyai/orca](https://github.com/stablyai/orca) es un entorno de desarrollo de agentes. Lanza
   otros coding agents y separa su estado Git mediante worktrees. El bucle sigue perteneciendo a
   Codex, Claude Code, OpenCode, Pi u otro proceso delegado.
2. [VirtusLab/orca](https://github.com/VirtusLab/orca) expresa flujos de desarrollo en etapas Scala.
   Las etapas son reanudables y los roles de planificación, implementación y revisión delegan en
   backends de agentes configurables.
3. [echoVic/orca-agent](https://github.com/echoVic/orca-agent) sí es un coding agent de terminal. Es
   un proyecto de tercero; «DeepSeek-native» no significa que pertenezca a DeepSeek.

Por tanto, Pi frente a Orca de stablyai no responde «qué harness es mejor». Las comparaciones válidas
son Pi frente a otro runtime bajo el mismo task contract, o Pi dentro de Orca frente a Pi sin esa
orquestación para medir aislamiento y overhead. El lab 03 rechaza la primera pregunta y acepta la
segunda como prueba de composición.

## 4. Cinco tesis de diseño que sí se pueden contrastar

### Reemplazabilidad profunda

La arquitectura oficial de `dsh` convierte en plugins el adaptador de modelo, el registro de tools,
el log de sesión y el loop. Además, deriva el historial visible para el modelo de un stream de
eventos duradero. Esto crea un seam experimental valioso: modificar un loop sin hacer fork del resto
del producto. La contrapartida es que la configuración efectiva, no el nombre del binario, define el
harness ejecutado.

### Superficie mínima

Pi entrega por defecto `read`, `write`, `edit` y `bash`, permite modificar la selección y deja
compaction, tools y extensiones abiertos. Esa austeridad reduce schemas iniciales, pero no constituye
una frontera de seguridad: su propia documentación dice que el proceso hereda acceso a filesystem,
red, credenciales y procesos. Minimalismo de prompt y mínimo privilegio son propiedades distintas.

### Protocolo textual como baseline

Aider mantiene familias explícitas de formatos de edición, como fichero completo, bloques de
búsqueda/reemplazo y unified diff. No debes puntuar como «tool call fallida» una respuesta que nunca
usó ese protocolo. Sí puedes comparar el outcome de la misma reparación, pero la conclusión será
sobre el sistema completo y debe conservar tokens, intentos de aplicación y conflictos del patch.

### Persistencia como tratamiento experimental

Hermes y OpenHarness incorporan memoria o aprendizaje que excede un run. Para medirlo, la condición
de control debe ejecutar dos sesiones sin memoria y la condición tratada dos sesiones con una
política de retención declarada. El segundo task debe ser análogo, no idéntico; de lo contrario se
mide memorización de la solución. Las entradas de memoria forman parte del dataset auditable.

### Orquestación por encima del loop

El Orca de stablyai propone candidatos paralelos en worktrees; el de VirtusLab convierte plan,
implementación y revisión en etapas deterministas y reanudables. Ninguno mejora mágicamente una
llamada al modelo. Pueden mejorar el outcome por selección, especialización o recuperación, pagando
más cómputo, coordinación y superficie de efectos. Esos costes pertenecen al resultado.

## 5. El contexto ambiente también es una variable

Un IDE puede aportar ficheros abiertos, selección, diagnósticos LSP y estado del editor que un TUI
no observa. Una app persistente puede recordar conversaciones que un CLI headless no recibe. Un ADE
puede ofrecer cinco candidatos cuando el baseline solo ejecuta uno.

Antes de comparar, registra:

- superficie exacta: CLI, TUI, IDE, app, API o headless;
- contexto inicial y reglas de descubrimiento;
- tools visibles, schemas completos y política de aprobación;
- filesystem, worktree, variables, credenciales y política de red;
- memoria, caches, historial y estado que atraviesan sesiones;
- quién compacta, cuándo lo hace y qué evidencia descarta;
- proceso humano: prompts adicionales, approvals, selección y merge.

Si no puedes igualar una variable, no ocultes la diferencia. Declárala como confounder y limita la
afirmación a «este sistema completo obtuvo este outcome bajo estas condiciones».

## 6. Seguridad: dónde termina el marketing

Un worktree separa ramas y directorios Git; no separa por sí solo red, llavero, procesos, variables
de entorno ni servicios compartidos. Un diálogo de approval puede mejorar supervisión; no sustituye
una comprobación de permisos en el executor. Un endpoint compatible puede aceptar mensajes; no
demuestra que reproduzca semántica de tools, streaming, caché o errores del proveedor original.

Para adoptar un harness, traza al menos estas fronteras:

1. qué código se instala y qué scripts de instalación ejecuta;
2. dónde persiste sesiones, prompts, trazas, memoria y credenciales;
3. qué telemetría o red externa usa en configuración mínima;
4. con qué identidad crea procesos y accede al filesystem;
5. qué acciones saltan approval y quién puede cambiar esa política;
6. cómo se revoca una sesión, se limpia el estado y se demuestra la limpieza.

«Open source», «local» y «sandboxed» responden preguntas diferentes. Verifica las tres por separado.

## 7. Cómo mantener vivo el panorama

Una actualización aceptable del catálogo necesita una fuente primaria, fecha de revisión y una
diferencia arquitectónica concreta. No aceptes una ficha copiada de una landing ni una afirmación de
rendimiento sin trials.

El pull request debe:

- enlazar repo y documentación oficial;
- asignar capa, cohorte y seam de composición;
- separar hechos verificables de hipótesis de benchmark;
- declarar superficie, loop, protocolo, portabilidad y trust boundary;
- añadir un caso que rompa si dos productos homónimos se fusionan;
- evitar estrellas, adjetivos de madurez y modelos efímeros como evidencia de calidad.

Codex CLI, Gemini CLI, Qwen Code y nuevos runtimes son candidatos obvios para ampliar el conjunto,
pero deben atravesar ese mismo proceso. SOTA no significa fingir exhaustividad: significa que el
método detecta una arquitectura nueva, actualiza la evidencia y no conserva como verdad lo que dejó
de verificarse.

## Fuentes primarias de esta lectura

- [DeepSeek Harness — arquitectura](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)
- [Pi Agent Harness — paquetes, permisos y aislamiento](https://github.com/earendil-works/pi)
- [Aider — edit formats](https://aider.chat/docs/more/edit-formats.html)
- [Hermes Agent](https://github.com/NousResearch/hermes-agent)
- [OpenHarness](https://github.com/HKUDS/OpenHarness)
- [Orca de stablyai](https://github.com/stablyai/orca)
- [Orca de VirtusLab](https://github.com/VirtusLab/orca)
- [Orca Agent de echoVic](https://github.com/echoVic/orca-agent)
- [OpenCode](https://github.com/anomalyco/opencode)
- [Goose](https://github.com/aaif-goose/goose)
- [Crush](https://github.com/charmbracelet/crush)
- [Claude Code](https://github.com/anthropics/claude-code)
- [Kilo Code](https://github.com/Kilo-Org/kilocode)
- [Cline](https://github.com/cline/cline)
- [Continue](https://github.com/continuedev/continue)
