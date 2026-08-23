# Guía de demo y revisión técnica

El objetivo no es enseñar todas las pantallas, sino probar la cadena problema → decisión →
comportamiento → evidencia → límite. Prepara una versión breve y otra profunda; la duración depende
del contexto de revisión, no de un formato académico. Ensáyala con un plan de contingencia que no
dependa de improvisar.

## Guion de referencia

| Minuto | Contenido | Evidencia visible |
|---:|---|---|
| 0–2 | usuario, dolor, alcance y no-objetivos | una frase y un caso realista |
| 2–4 | arquitectura y dos decisiones clave | diagrama + ADRs |
| 4–7 | happy path RAG/agente | respuesta, citas y tool trace |
| 7–10 | caso difícil/fuera de corpus | abstención o aclaración correcta |
| 10–12 | ataque o tool error | control, salida degradada, sin side effect |
| 12–14 | aprobación/reanudación | checkpoint y actor de aprobación |
| 14–16 | eval y ablation | resultado por caso, no solo media |
| 16–18 | producción | dashboard, uptime, p95 y alerta probada |
| 18–19 | coste | coste/tarea y proyección 10× |
| 19–20 | límites y siguiente decisión | dos fallos conocidos priorizados |

No escribas código en vivo. Lleva las queries preparadas en un fichero versionado y restablece el
estado antes del ensayo. Enseña al menos un fallo: una demo que solo funciona no demuestra que el
sistema sepa fallar.

## Plan de contingencia

- vídeo/captura reciente de máximo tres minutos para caída del proveedor o cloud;
- resultados y dashboard exportados con timestamp y commit;
- modo offline contra fixtures para demostrar grafo, tools y errores;
- segunda red y credenciales comprobadas sin mostrarlas;
- comando de rollback y versión anterior disponible;
- una diapositiva que declara qué parte es live y cuál evidencia grabada.

No presentes una grabación antigua como live. Si algo falla, abre la traza, explica el límite y usa
el fallback: diagnosticar bien durante la demo suma más que ocultar el incidente.

## Checklist del ensayo

- dos ensayos completos por debajo de 19 minutos;
- otra persona formula cinco preguntas no preparadas;
- enlaces, login y monitor probados desde perfil/navegador limpio;
- datos de demo sin PII y side effects reversibles;
- caches calentadas o declaradas; cold start medido;
- zoom/tamaño legible y notificaciones silenciadas;
- commit/digest final anotado y feature freeze activo.

## Preguntas de revisión

Prepara respuestas con números y artefactos propios. “Es una best practice” no justifica una
decisión.

### Problema y arquitectura

1. ¿Qué usuario concreto no podría sustituir esto por búsqueda tradicional?
2. ¿Qué parte del problema decidiste no resolver y por qué?
3. ¿Cuál es el primer cuello de botella a 10× y qué métrica lo demuestra?
4. ¿Por qué un agente y no una cadena determinista?
5. ¿Qué eliminarías si tuvieras que reducir la complejidad a la mitad?
6. ¿Qué ADR cambió más entre la hipótesis inicial y la versión medida?
7. ¿Qué dependencia externa tiene mayor blast radius y cómo la aíslas?

### RAG y evaluación

8. ¿Cómo sabes que el corpus contiene la respuesta antes de culpar al retrieval?
9. ¿Por qué elegiste ese chunking y qué ablation lo sostiene?
10. ¿Qué diferencia hay entre recuperar el documento correcto y el chunk correcto?
11. ¿Dónde falla tu reranker y cuánto añade a p95?
12. ¿Cómo se comporta ante una pregunta fuera de corpus?
13. ¿Qué cinco casos tienen peor faithfulness y cuál es su causa raíz?
14. ¿Cuánta varianza tiene tu juez y qué auditaste manualmente?
15. ¿Qué impide que una cita válida respalde una afirmación falsa?
16. ¿Cómo invalidas el índice cuando cambia parser, chunker o embedding?

### Agente y tools

17. ¿Qué estado y arista impiden un bucle infinito?
18. ¿Cuál es el contrato de error de cada herramienta?
19. ¿Cómo pruebas idempotencia cuando la respuesta se pierde tras el commit?
20. ¿Qué acciones exigen confirmación y a qué argumentos queda ligada?
21. ¿Puede un documento recuperado activar una tool? ¿Qué control lo impide?
22. ¿Por qué tu diseño multi-agente mejora al baseline de un solo agente?
23. ¿Cómo reanudas una tarea tras reinicio sin repetir side effects?
24. ¿Qué memoria guardas, durante cuánto y cómo atiendes un borrado?

### Producción, seguridad y operación

25. ¿Cómo se calculó exactamente el p95 y cuál fue la carga?
26. ¿Qué diferencia hay entre `/health`, `/ready` y task success?
27. ¿Qué alerta probaste y cuánto tardó en detectar/recuperar?
28. ¿Qué hay en tus trazas que podría ser dato personal?
29. ¿Cómo rotas un secreto filtrado y cómo sabes dónde se usó?
30. ¿Qué ocurre si el proveedor devuelve 429 durante diez minutos?
31. ¿Cómo haces rollback de modelo/prompt/corpus además del código?
32. ¿Qué ataque del threat model no has mitigado todavía?
33. ¿Cómo evitas que un tenant vea cache, memoria o chunks de otro?
34. ¿Qué artefactos verifican que la imagen desplegada es la revisada?

### Modelos, coste y decisión

35. ¿Qué modelos y snapshots exactos corriste, y cuándo verificaste el catálogo?
36. ¿Por qué esa ruta usa Luna/Terra/Sol —o tus tiers actuales— y no otra?
37. ¿Qué pasa con calidad, coste y p95 si fuerzas el tier más pequeño?
38. ¿Cuál es el coste p95 por tarea exitosa, incluidos retries y evals?
39. ¿A qué volumen sale a cuenta self-host y qué coste operativo incluiste?
40. ¿Qué supuesto de tu proyección 100× es más frágil?
41. Si mañana retiran tu modelo, ¿qué gate decide el sustituto?
42. ¿Cuál sería la siguiente decisión con datos de producción reales?

## Cómo responder

Usa la secuencia **decisión → alternativa → evidencia → límite**:

> Elegimos recuperación híbrida porque las consultas con IDs fallaban con semántica sola. En 50
> casos, recall@4 subió del resultado A al B con X ms en p95. Descartamos semántica pura; el límite
> es que el índice lexical añade operación e invalidación, documentadas en ADR-003.

Sustituye A/B/X por tus resultados reales. Si no mediste algo, dilo y explica el experimento que
harías; inventar una cifra destruye credibilidad.

## Code review de cierre

Ten listos cinco puntos: entrada HTTP hasta respuesta, router del grafo, una tool con error e
idempotencia, retrieval+citas y telemetría. El revisor puede elegir cualquier línea: elimina código
muerto, dependencias innecesarias y secretos antes de congelar la versión.
