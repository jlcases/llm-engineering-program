# Project Proposals

Five projects ready to adopt. All five meet the capstone requirements (a corpus with sufficient volume for RAG to be meaningful, an agent whose tools are not merely decorative, and a use case that offers ample material for the defense). Choose based on affinity with the domain: you will be spending 6 weeks inside it.

Common corpus size criterion: **between 200 and 2,000 source documents** (or 1,000–20,000 chunks). Fewer, and retrieval is trivial (a grep would suffice); more, and ingestion eats up the schedule.

---

## 1. Technical Regulation Assistant — "Does my project comply with the CTE?"

**Domain.** Queries about the Spanish Technical Building Code (CTE) (or an equivalent regulatory body: GDPR + AEPD, traffic regulations, collective bargaining agreements in a specific sector).

**Corpus.** The CTE Basic Documents are public PDFs, long (several hundred pages each), with tables, formulas, and cross-references between sections. It is a difficult corpus *in the right sense*: it will test your PDF extraction, table chunking, and handling of references ("as established in DB-SI 3, section 4").

**Agent Tools.**
1. `buscar_normativa(query, documento_basico?)` — retrieval over the index, with optional filtering by DB.
2. `calcular(expresion, contexto)` — evaluator of regulatory formulas (occupancy, evacuation routes, minimum toilet provision) with the norm's constants; forces the agent to decide *when* the answer requires calculation and not just citation.
3. `verificar_vigencia(seccion)` — query against a table of modifications/abolitions that you maintain (the DBs have versions); teaches the agent not to respond with abolished regulations.

**Why it is a good capstone.** The domain penalizes hallucinations visibly (citing a non-existent article is an objective failure, not a matter of taste), making faithfulness the star metric and providing excellent material for the defense. The evaluation dataset is well-constructed: questions with literal answers in the regulation.

**Risk to monitor.** PDF table extraction can eat up week 2. Do an extraction spike with 3 documents before committing; if Docling/unstructured do not extract tables decently, switch to an HTML regulatory body (consolidated BOE).

---

## 2. Copilot for Support on Real Product Documentation

**Domain.** Level 1–2 technical support for the public documentation of a specific software product (choose one with large, high-quality docs: PostgreSQL, Kubernetes, Stripe, Terraform, Home Assistant).

**Corpus.** The complete official documentation, crawled and ingested (Markdown/HTML, with significant embedded code). Between 500 and 2,000 pages depending on the product. Chunking code blocks alongside their prose is the key technical challenge.

**Agent Tools.**
1. `buscar_docs(query, version?)` — retrieval with product version filtering (answers valid for PG 16 may be incorrect for PG 12).
2. `ejecutar_snippet(codigo)` — sandbox (ephemeral container or Piston-like service) where the agent validates that the example it is about to provide actually works; this is the tool that impresses most in demos.
3. `buscar_issues(query)` — search within the product's GitHub issues via API, for questions like "is this a known bug?".

**Why it is a good capstone.** It is the most commercially viable use case on the market (every SaaS wants this) and allows you to benchmark your answers against an external source of truth: accepted answers on Stack Overflow for the same product can be used to validate your evaluation dataset.

**Risk to monitor.** `ejecutar_snippet` is a real security vector: mandatory sandbox, timeout, no network access. If you are not going to implement it properly, replace it with `validar_config(fichero)` (static configuration linting), which is safer and still useful.

---

## 3. Public Procurement File Analyst

**Domain.** Questions regarding public tenders: "what technical solvency is required?", "which award criterion carries the most weight?", "compare these two tender specifications".

**Corpus.** Tender specifications (PCAP and PPT) downloaded from the Public Sector Procurement Platform, filtered by a specific sector (e.g., IT services). 200–500 files, each containing 2–4 PDFs. Public data, zero legal risk.

**Agent Tools.**
1. `buscar_pliegos(query, filtros)` — retrieval with metadata (authority, amount, CPV code, date).
2. `extraer_estructurado(expediente_id)` — extraction using structured outputs (Pydantic) of the key specification fields: budget, deadlines, criteria and weights, solvency. Connects directly with what was learned in Module 2.
3. `comparar_expedientes(ids)` — generates a comparative table from the structured extractions; a composition tool, not a retrieval tool, demonstrating true orchestration.

**Why it is a good capstone.** Combines RAG with structured extraction (two disciplines evaluable separately), the target user is very clear (companies bidding), and the cost analysis has a natural business narrative: analyzing each tender specification manually costs hours of a technician's time.

**Risk to monitor.** Brutal heterogeneity between specifications (each authority writes its own). Constrain it: a single contract type and a single sector. Corpus homogeneity is your friend in 6 weeks.

---

## 4. Medical-sporting second brain based on training literature

**Domain.** Questions on evidence in sports science and nutrition: "what does the evidence say about fasting training?", "supported creatine dosages".

**Corpus.** Open-access abstracts and papers from PubMed Central on a bounded subfield (e.g., strength training + supplementation), 500–1,500 papers. The PubMed API enables programmatic and reproducible ingestion.

**Agent tools.**
1. `buscar_evidencia(query, tipo_estudio?)` — retrieval with filtering by type (RCT, meta-analysis, observational).
2. `evaluar_calidad(paper_id)` — returns study quality signals (n, type, year, whether it is a meta-analysis) from the metadata you indexed; the agent must weigh the evidence, not just cite it.
3. `buscar_pubmed_reciente(query)` — live query to the PubMed API for literature post-dating your ingestion cutoff; demonstrates the index-self + live-source combination, a highly defensible architectural pattern.

**Why it is a good capstone.** It forces a serious and demonstrable guardrail: the system must refuse to give personalized medical advice and stick to summarizing evidence with citations. That guardrail, attacked during the demo with adversarial prompts, is gold for the defense. Furthermore, faithfulness on scientific literature is a very clean evaluation case.

**Risk to watch.** The temptation for the agent to "recommend". Define the exact boundary (inform yes, prescribe no) in an ADR and test it with a dataset of adversarial prompts starting from week 3.

---

## 5. Junior on-call engineer — runbook and incident assistant

**Domain.** On-call assistant based on the operational documentation of an infrastructure: "Redis is at 95% memory, what do I do?", "which services depend on the payment gateway?".

**Corpus.** If you have access to real runbooks (anonymized), perfect. If not: generate a synthetic-realistic corpus from a fictional company (40–60 runbooks, 30 postmortems, 15–20 services' architecture docs) using an LLM with your manual review, and declare it openly. A *well-constructed and documented* synthetic corpus is defensible; an improvised one is not.

**Agent tools.**
1. `buscar_runbooks(query, servicio?)` — retrieval on runbooks and postmortems.
2. `estado_servicio(nombre)` — live metric query from a toy infrastructure you deploy (2–3 containers with Prometheus); allows spectacular demos: you break a service live and the agent diagnoses it.
3. `crear_incidente(resumen, severidad)` — opens a GitHub issue with the incident template filled out; a *writing* tool with human confirmation, which forces you to implement true human-in-the-loop.

**Why it's a good capstone.** It is the only one of the five where the agent acts on the world (not just reads), so error handling, tool permissions, and human-in-the-loop cease to be theory. The live incident demo is the most memorable of the five proposals.

**Risk to watch.** Double deployment (the capstone system + the monitored toy infrastructure). Keep the toy infrastructure minimal: docker-compose with 3 services on the same cheap VM is sufficient.

---

## Do you prefer to propose your own project?

Go ahead; it usually turns out better if the domain is yours. It must pass this filter before week 1 (answer it in writing; it is the first page of your architecture document):

1. **Corpus**: Does it already exist, is it legal to use, and is it in the 200–2,000 documents band? If you have to create it, can you create it well in less than a week?
2. **Retrieval merit**: Are there questions whose answer requires *combining or locating* non-trivial information? If every question can be answered with the first result of a keyword search, RAG will not shine.
3. **Three tools with distinct roles**: at least one for retrieval, one for computation/transformation, and one for action or a live external source. Three variants of search do not count as three tools.
4. **Objective evaluation**: Can you write 50 questions with verifiable reference answers against the corpus? If answer quality is a matter of opinion, RAGAS will not save you.
5. **Named user**: Can you say in one sentence who would use it and what it costs them today not to have it? (You will need this for the cost analysis and for the defense.)
6. **20-minute demo**: Is the use case understandable without explaining 10 minutes of domain context?

If you are unsure between two, choose the one with the most boring corpus and the clearest tools. Capstones die from exotic corpora, not from dull domains.
