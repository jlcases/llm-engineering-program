# Propuestas de proyecto

Cinco puntos de partida, no cinco enunciados cerrados. Todos exigen un corpus donde el retrieval tenga
mérito, capacidades que produzcan un efecto verificable y un caso de uso que sobreviva a una revisión
con evidencia. Elige por afinidad con el problema y reduce el alcance hasta poder entregar una
vertical real pronto.

Criterio orientativo de tamaño de corpus: **entre 200 y 2.000 documentos-fuente** (o 1.000–20.000
chunks). Por debajo, demuestra que retrieval mejora a `grep`; por encima, presupuesta la ingestión y
la evaluación antes de ampliar alcance.

---

## 1. Asistente de normativa técnica — "¿Cumple mi proyecto el CTE?"

**Dominio.** Consultas sobre el Código Técnico de la Edificación español (o un cuerpo normativo equivalente: RGPD + AEPD, normativa de tráfico, convenios colectivos de un sector).

**Corpus.** Los Documentos Básicos del CTE son PDFs públicos, largos (varios cientos de páginas cada uno), con tablas, fórmulas y referencias cruzadas entre secciones. Es un corpus difícil *en el sentido correcto*: pondrá a prueba tu extracción de PDF, el chunking de tablas y el manejo de referencias ("según se establece en el DB-SI 3, apartado 4").

**Herramientas del agente.**
1. `buscar_normativa(query, documento_basico?)` — retrieval sobre el índice, con filtro opcional por DB.
2. `calcular(expresion, contexto)` — evaluador de fórmulas normativas (ocupación, recorridos de evacuación, dotación mínima de aseos) con las constantes de la norma; obliga al agente a decidir *cuándo* la respuesta requiere cálculo y no solo cita.
3. `verificar_vigencia(seccion)` — consulta contra una tabla de modificaciones/derogaciones que tú mantienes (los DB tienen versiones); enseña al agente a no responder con normativa derogada.

**Por qué es buen proyecto de campo.** El dominio castiga las alucinaciones de forma visible (citar
un artículo inexistente es un fallo objetivo, no de gusto), permite evaluar soporte de claims y
produce preguntas con respuesta verificable en la norma.

**Riesgo a vigilar.** La extracción de tablas de PDF puede bloquear todo el proyecto. Haz un spike con
3 documentos antes de comprometerte; si Docling/unstructured no sacan las tablas decentemente,
cambia a un cuerpo normativo en HTML (BOE consolidado).

---

## 2. Copiloto de soporte sobre documentación de producto real

**Dominio.** Soporte técnico nivel 1–2 sobre la documentación pública de un producto software concreto (elige uno con docs grandes y buenas: PostgreSQL, Kubernetes, Stripe, Terraform, Home Assistant).

**Corpus.** La documentación oficial completa, rastreada e ingerida (Markdown/HTML, mucho código embebido). Entre 500 y 2.000 páginas según el producto. El chunking de bloques de código junto a su prosa es el reto técnico diferencial.

**Herramientas del agente.**
1. `buscar_docs(query, version?)` — retrieval con filtro por versión del producto (las respuestas válidas para PG 16 pueden ser erróneas en PG 12).
2. `ejecutar_snippet(codigo)` — sandbox (contenedor efímero o servicio tipo Piston) donde el agente valida que el ejemplo que va a dar realmente funciona; es la herramienta que más impresiona en demo.
3. `buscar_issues(query)` — búsqueda en los issues de GitHub del producto vía API, para preguntas del tipo "¿es un bug conocido?".

**Por qué es buen proyecto de campo.** Es el caso de uso más contratable del mercado (todo SaaS quiere esto) y permite comparar tus respuestas contra una fuente de verdad externa: las respuestas aceptadas de Stack Overflow sobre el mismo producto sirven para validar tu dataset de evaluación.

**Riesgo a vigilar.** `ejecutar_snippet` es un vector de seguridad real: sandbox obligatorio, timeout, sin red. Si no vas a hacerlo bien, sustitúyela por `validar_config(fichero)` (lint estático de configuración), que es más segura y sigue siendo útil.

---

## 3. Analista de expedientes de contratación pública

**Dominio.** Preguntas sobre licitaciones públicas: "¿qué solvencia técnica piden?", "¿cuál es el criterio de adjudicación con más peso?", "compárame estos dos pliegos".

**Corpus.** Pliegos (PCAP y PPT) descargados de la Plataforma de Contratación del Sector Público, filtrados por un sector (p. ej. servicios TI). 200–500 expedientes, cada uno con 2–4 PDFs. Datos públicos, cero problema legal.

**Herramientas del agente.**
1. `buscar_pliegos(query, filtros)` — retrieval con metadatos (órgano, importe, CPV, fecha).
2. `extraer_estructurado(expediente_id)` — extracción con structured outputs (Pydantic) de los campos clave del pliego: presupuesto, plazos, criterios y pesos, solvencia. Conecta directamente con lo aprendido en el módulo 2.
3. `comparar_expedientes(ids)` — genera una tabla comparativa a partir de las extracciones estructuradas; herramienta de composición, no de retrieval, lo que demuestra orquestación real.

**Por qué es buen proyecto de campo.** Combina RAG con extracción estructurada (dos disciplinas evaluables por separado), el usuario objetivo es clarísimo (empresas que licitan) y el análisis de costes tiene una narrativa de negocio natural: cada pliego analizado a mano cuesta horas de un técnico.

**Riesgo a vigilar.** Heterogeneidad brutal entre pliegos (cada órgano escribe el suyo). Acótalo: un
solo tipo de contrato y un solo sector. La homogeneidad del corpus protege la calidad y el plazo.

---

## 4. Segundo cerebro médico-deportivo sobre literatura de entrenamiento

**Dominio.** Preguntas sobre evidencia en ciencias del deporte y nutrición: "¿qué dice la evidencia sobre entrenar en ayunas?", "dosis de creatina con respaldo".

**Corpus.** Abstracts y papers en abierto de PubMed Central sobre un subcampo acotado (p. ej. entrenamiento de fuerza + suplementación), 500–1.500 papers. La API de PubMed hace la ingestión programática y reproducible.

**Herramientas del agente.**
1. `buscar_evidencia(query, tipo_estudio?)` — retrieval con filtro por tipo (RCT, metaanálisis, observacional).
2. `evaluar_calidad(paper_id)` — devuelve señales de calidad del estudio (n, tipo, año, si es metaanálisis) desde metadatos que indexaste; el agente debe ponderar la evidencia, no solo citarla.
3. `buscar_pubmed_reciente(query)` — consulta en vivo a la API de PubMed para literatura posterior a tu corte de ingestión; demuestra la combinación índice-propio + fuente-viva, un patrón de arquitectura muy defendible.

**Por qué es buen proyecto de campo.** Obliga a una frontera de autoridad seria y demostrable: el
sistema debe negarse a dar consejo médico personalizado y ceñirse a resumir evidencia con citas. Esa
frontera se prueba con prompts adversarios y falsos positivos, no solo con una instrucción.

**Riesgo a vigilar.** La tentación de que el agente "recomiende". Define la frontera exacta (informar
sí, prescribir no) en un ADR y conviértela desde el primer corte funcional en un dataset de prompts
adversarios.

---

## 5. Ingeniero de guardia junior — asistente de runbooks e incidentes

**Dominio.** Asistente de on-call sobre la documentación operativa de una infraestructura: "Redis está a 95% de memoria, ¿qué hago?", "¿qué servicios dependen del gateway de pagos?".

**Corpus.** Si tienes acceso a runbooks reales (anonimizados), perfecto. Si no: genera un corpus sintético-realista de una empresa ficticia (40–60 runbooks, 30 postmortems, docs de arquitectura de 15–20 servicios) usando un LLM con revisión manual tuya, y decláralo abiertamente. Un corpus sintético *bien construido y documentado* es defendible; uno improvisado, no.

**Herramientas del agente.**
1. `buscar_runbooks(query, servicio?)` — retrieval sobre runbooks y postmortems.
2. `estado_servicio(nombre)` — consulta métricas en vivo de una infraestructura de juguete que tú despliegas (2–3 contenedores con Prometheus); permite demos espectaculares: rompes un servicio en vivo y el agente lo diagnostica.
3. `crear_incidente(resumen, severidad)` — abre un issue en GitHub con la plantilla de incidente rellenada; herramienta de *escritura* con confirmación humana, lo que te obliga a implementar human-in-the-loop de verdad.

**Por qué es buen proyecto de campo.** Es el único de los cinco donde el agente actúa sobre el mundo (no solo lee), así que el manejo de errores, los permisos por herramienta y el human-in-the-loop dejan de ser teoría. La demo con incidente en vivo es la más memorable de las cinco propuestas.

**Riesgo a vigilar.** Doble despliegue (el sistema del proyecto de campo + la infra de juguete monitorizada). Mantén la infra de juguete mínima: docker-compose con 3 servicios en la misma VM barata basta.

---

## ¿Prefieres proponer tu propio proyecto?

Adelante, suele salir mejor si el dominio es tuyo. Antes de construir, responde este filtro por
escrito como primera página de tu documento de arquitectura:

1. **Corpus**: ¿existe ya, es legal usarlo, y está en la banda 200–2.000 documentos? Si tienes que
   fabricarlo, ¿puedes hacerlo bien sin consumir la mayor parte del esfuerzo?
2. **Mérito del retrieval**: ¿hay preguntas cuya respuesta exige *combinar o localizar* información no trivial? Si toda pregunta se responde con el primer resultado de una búsqueda por palabras clave, el RAG no lucirá.
3. **Tres herramientas con papeles distintos**: como mínimo una de retrieval, una de cómputo/transformación y una de acción o fuente externa viva. Tres variantes de búsqueda no cuentan como tres herramientas.
4. **Evaluación objetiva**: ¿puedes escribir 50 preguntas con respuesta de referencia verificable contra el corpus? Si la calidad de las respuestas es cuestión de opinión, RAGAS no te va a salvar.
5. **Usuario nombrable**: ¿puedes decir en una frase quién lo usaría, qué decisión toma y qué le
   cuesta hoy no tenerlo?
6. **Prueba breve**: ¿el caso de uso se entiende y demuestra con evidencia sin una introducción larga
   sobre el dominio?

Si dudas entre dos, elige la de corpus más aburrido y herramientas más claras. Los proyectos de campo mueren por corpus exóticos, no por dominios sosos.
