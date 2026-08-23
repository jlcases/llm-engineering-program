# 01 — Tres grafos y sus invariantes

«Usamos un grafo» no describe una arquitectura. Debes decir qué representa un nodo, qué afirma una
arista, quién puede crearla y qué consulta necesita atravesarla.

## 1. Cuándo un grafo es la estructura correcta

Usa un grafo cuando importan relaciones variables, caminos, vecindarios o conectividad. Prefiere:

- tabla relacional para joins conocidos y restricciones transaccionales;
- documento para agregados que se leen y escriben juntos;
- índice vectorial para similitud semántica;
- grafo para patrones de relación que cambian y consultas multi-hop.

Una arquitectura híbrida es normal. El error es esperar que un único almacén optimice todas las
consultas.

## 2. Grafo de ejecución

Representa control:

- nodo: transformación determinista, llamada a modelo, tool o aprobación;
- arista: transición permitida bajo una condición;
- estado: snapshot tipado compartido;
- reducer: regla para incorporar updates;
- terminal: condición explícita de parada.

Sus invariantes incluyen nodos alcanzables, transición válida, reducer compatible, límites de ciclo
y persistencia antes de un interrupt. El éxito se mide por outcome y trayectoria, no por densidad.

## 3. Grafo de conocimiento

Representa afirmaciones del dominio:

- entidad con identidad estable;
- tipo y propiedades versionadas;
- relación semántica dirigida;
- evento con tiempo y participantes;
- alias o mención enlazado a una entidad resuelta.

Una arista `company_acquired_company` no es equivalente a `mentions`. Define dirección,
cardinalidad, vigencia y si puede coexistir con una relación contradictoria.

## 4. Grafo de procedencia

Representa por qué el sistema cree o hizo algo:

- fuente y versión;
- pasaje o registro exacto;
- claim normalizado;
- relación `supports`, `contradicts` o `derived_from`;
- decisión, actor y política aplicada;
- artefacto o efecto resultante.

Permite responder «¿qué evidencia cambiaría esta conclusión?» y retirar claims cuando una fuente se
revoca sin borrar historia.

## 5. Tipos e identidad

Antes de elegir base de datos, define:

```text
NodeId = namespace + canonical_key + version_policy
EdgeId = source + predicate + target + valid_time + evidence_set
```

La identidad no debe depender de la redacción del modelo. Normaliza con claves de negocio, registros
autoritativos y reglas deterministas. Cuando la resolución sea incierta, conserva menciones separadas
y una relación candidata con confianza y evidencia.

## 6. Invariantes útiles

- endpoints existen y cumplen tipos permitidos;
- toda arista factual tiene uno o más evidence IDs;
- cardinalidad se verifica al escribir;
- ciclos prohibidos se detectan antes de commit;
- tiempo válido y tiempo de registro no se confunden;
- borrar una fuente invalida derivados sin borrar auditoría;
- un path devuelto conserva cada arista y su procedencia.

Aplica invariantes en la frontera de escritura. Pedir al generador que «cree un grafo coherente» no
protege el sistema.

## 7. Framework frente a modelo conceptual

LangGraph puede ejecutar un grafo de estado; Neo4j, Neptune o una tabla de edges pueden almacenar
conocimiento; un event store puede sostener procedencia. Ninguna librería define por ti identidad,
autoridad o verdad.

Diseña primero queries e invariantes. Después elige el motor que las ejecuta con la latencia,
consistencia y coste requeridos.
