# Project Proposals

Five starting points, not five closed assignments. Each requires a corpus where retrieval earns its
place, capabilities that produce a verifiable effect, and a use case that survives an evidence-based
review. Choose based on affinity with the problem and narrow the scope until you can ship a real
vertical slice early.

Indicative corpus size: **between 200 and 2,000 source documents** (or 1,000–20,000 chunks). Below
that, prove retrieval improves on `grep`; above it, budget ingestion and evaluation before expanding
scope.

---

## 1. Technical Regulation Assistant — "Does my project comply with the CTE?"

**Domain.** Queries about the Spanish Technical Building Code (CTE) (or an equivalent regulatory body: GDPR + AEPD, traffic regulations, collective bargaining agreements in a specific sector).

**Corpus.** The CTE Basic Documents are public PDFs, long (several hundred pages each), with tables, formulas, and cross-references between sections. It is a difficult corpus *in the right sense*: it will test your PDF extraction, table chunking, and handling of references ("as established in DB-SI 3, section 4").

**Agent Tools.**
1. `buscar_normativa(query, documento_basico?)` — retrieval over the index, with optional filtering by DB.
2. `calcular(expresion, contexto)` — evaluator of regulatory formulas (occupancy, evacuation routes, minimum toilet provision) with the norm's constants; forces the agent to decide *when* the answer requires calculation and not just citation.
3. `verificar_vigencia(seccion)` — query against a table of modifications/abolitions that you maintain (the DBs have versions); teaches the agent not to respond with abolished regulations.

**Why it is a good field project.** The domain penalizes hallucinations visibly (citing a
non-existent article is an objective failure, not a matter of taste), supports claim-level evidence
evaluation, and produces questions with verifiable answers in the regulation.

**Risk to monitor.** PDF table extraction can block the entire project. Run an extraction spike with
3 documents before committing; if Docling/unstructured do not extract tables decently, switch to an
HTML regulatory body (consolidated BOE).

---

## 2. Copilot for Support on Real Product Documentation

**Domain.** Level 1–2 technical support for the public documentation of a specific software product (choose one with large, high-quality docs: PostgreSQL, Kubernetes, Stripe, Terraform, Home Assistant).

**Corpus.** The complete official documentation, crawled and ingested (Markdown/HTML, with significant embedded code). Between 500 and 2,000 pages depending on the product. Chunking code blocks alongside their prose is the key technical challenge.

**Agent Tools.**
1. `buscar_docs(query, version?)` — retrieval with product version filtering (answers valid for PG 16 may be incorrect for PG 12).
2. `ejecutar_snippet(codigo)` — sandbox (ephemeral container or Piston-like service) where the agent validates that the example it is about to provide actually works; this is the tool that impresses most in demos.
3. `buscar_issues(query)` — search within the product's GitHub issues via API, for questions like "is this a known bug?".

**Why it is a good field project.** It is the most commercially viable use case on the market (every SaaS wants this) and allows you to benchmark your answers against an external source of truth: accepted answers on Stack Overflow for the same product can be used to validate your evaluation dataset.

**Risk to monitor.** `ejecutar_snippet` is a real security vector: mandatory sandbox, timeout, no network access. If you are not going to implement it properly, replace it with `validar_config(fichero)` (static configuration linting), which is safer and still useful.

---

## 3. Public Procurement File Analyst

**Domain.** Questions regarding public tenders: "what technical solvency is required?", "which award criterion carries the most weight?", "compare these two tender specifications".

**Corpus.** Tender specifications (PCAP and PPT) downloaded from the Public Sector Procurement Platform, filtered by a specific sector (e.g., IT services). 200–500 files, each containing 2–4 PDFs. Public data, zero legal risk.

**Agent Tools.**
1. `buscar_pliegos(query, filtros)` — retrieval with metadata (authority, amount, CPV code, date).
2. `extraer_estructurado(expediente_id)` — extraction using structured outputs (Pydantic) of the key specification fields: budget, deadlines, criteria and weights, solvency. Connects directly with what was learned in Module 2.
3. `comparar_expedientes(ids)` — generates a comparative table from the structured extractions; a composition tool, not a retrieval tool, demonstrating true orchestration.

**Why it is a good field project.** Combines RAG with structured extraction (two disciplines evaluable separately), the target user is very clear (companies bidding), and the cost analysis has a natural business narrative: analyzing each tender specification manually costs hours of a technician's time.

**Risk to monitor.** Brutal heterogeneity between specifications (each authority writes its own).
Constrain it to one contract type and one sector. Corpus homogeneity protects both quality and the
delivery window.

---

## 4. Medical-sporting second brain based on training literature

**Domain.** Questions on evidence in sports science and nutrition: "what does the evidence say about fasting training?", "supported creatine dosages".

**Corpus.** Open-access abstracts and papers from PubMed Central on a bounded subfield (e.g., strength training + supplementation), 500–1,500 papers. The PubMed API enables programmatic and reproducible ingestion.

**Agent tools.**
1. `buscar_evidencia(query, tipo_estudio?)` — retrieval with filtering by type (RCT, meta-analysis, observational).
2. `evaluar_calidad(paper_id)` — returns study quality signals (n, type, year, whether it is a meta-analysis) from the metadata you indexed; the agent must weigh the evidence, not just cite it.
3. `buscar_pubmed_reciente(query)` — live query to the PubMed API for literature post-dating your ingestion cutoff; demonstrates the index-self + live-source combination, a highly defensible architectural pattern.

**Why it is a good field project.** It forces a serious and demonstrable authority boundary: the
system must refuse personalized medical advice and stay within evidence summaries with citations.
That boundary is tested with adversarial prompts and false positives, not only an instruction.

**Risk to watch.** The temptation for the agent to "recommend." Define the exact boundary (inform,
yes; prescribe, no) in an ADR and turn it into an adversarial prompt dataset from the first working
slice.

---

## 5. Junior on-call engineer — runbook and incident assistant

**Domain.** On-call assistant based on the operational documentation of an infrastructure: "Redis is at 95% memory, what do I do?", "which services depend on the payment gateway?".

**Corpus.** If you have access to real runbooks (anonymized), perfect. If not: generate a synthetic-realistic corpus from a fictional company (40–60 runbooks, 30 postmortems, 15–20 services' architecture docs) using an LLM with your manual review, and declare it openly. A *well-constructed and documented* synthetic corpus is defensible; an improvised one is not.

**Agent tools.**
1. `buscar_runbooks(query, servicio?)` — retrieval on runbooks and postmortems.
2. `estado_servicio(nombre)` — live metric query from a toy infrastructure you deploy (2–3 containers with Prometheus); allows spectacular demos: you break a service live and the agent diagnoses it.
3. `crear_incidente(resumen, severidad)` — opens a GitHub issue with the incident template filled out; a *writing* tool with human confirmation, which forces you to implement true human-in-the-loop.

**Why it's a good field project.** It is the only one of the five where the agent acts on the world (not just reads), so error handling, tool permissions, and human-in-the-loop cease to be theory. The live incident demo is the most memorable of the five proposals.

**Risk to watch.** Double deployment (the field project system + the monitored toy infrastructure). Keep the toy infrastructure minimal: docker-compose with 3 services on the same cheap VM is sufficient.

---

## Do you prefer to propose your own project?

Go ahead; it usually turns out better if the domain is yours. Before building, answer this filter in
writing as the first page of your architecture document:

1. **Corpus**: Does it already exist, is it legal to use, and is it in the 200–2,000 document band? If
   you must create it, can you do so well without consuming most of the effort?
2. **Retrieval merit**: Are there questions whose answer requires *combining or locating* non-trivial information? If every question can be answered with the first result of a keyword search, RAG will not shine.
3. **Three tools with distinct roles**: at least one for retrieval, one for computation/transformation, and one for action or a live external source. Three variants of search do not count as three tools.
4. **Objective evaluation**: Can you write 50 questions with verifiable reference answers against the corpus? If answer quality is a matter of opinion, RAGAS will not save you.
5. **Named user**: Can you say in one sentence who would use it, which decision they make, and what
   it costs them today not to have it?
6. **Short proof**: Can someone understand the use case and see the evidence without a long domain
   introduction?

If you are unsure between two, choose the one with the most boring corpus and the clearest tools. Field projects die from exotic corpora, not from dull domains.
