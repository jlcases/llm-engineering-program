# Documento de arquitectura — [Nombre del proyecto]

> **Cómo usar esta plantilla.** Sustituye cada bloque de instrucciones por tu contenido y bórralo.
> La longitud la decide la evidencia, no un número de páginas. Un documento de arquitectura registra
> decisiones y trade-offs; cada decisión costosa o difícil de revertir va a un ADR
> ([formato aquí](plantilla-adr.md)).

**Versión:** v1.0 · **Fecha:** AAAA-MM-DD · **Autor:** [nombre] · **Estado:** borrador / en revisión / aprobado

---

## 1. Contexto y problema

> Identifica usuario, JTBD, coste actual y outcome. Termina con una frase de alcance negativo: qué
> **no** hace el sistema y qué riesgo evita esa frontera.

## 2. Requisitos

### 2.1 Funcionales

> Lista numerada (RF-1, RF-2…) de capacidades observables por el usuario. Cada una en una frase verificable. Ejemplo del estilo esperado: "RF-3: ante una pregunta cuya respuesta no esté en el corpus, el sistema lo dice explícitamente y no inventa" — nótese que es testeable.

### 2.2 No funcionales (con número, no con adjetivo)

| ID | Requisito | Objetivo | Cómo se mide |
|---|---|---|---|
| RNF-1 | Latencia del outcome | [objetivo predefinido] | Test de carga desde la interfaz real |
| RNF-2 | Disponibilidad | [SLO + ventana] | Monitor externo |
| RNF-3 | Soporte de claims | [gate por segmento/riesgo] | Eval harness + auditoría humana |
| RNF-4 | Coste por outcome | < [tu objetivo] € | Usage receipts con tarifas versionadas |
| RNF-5 | Autoridad | Ningún efecto fuera del capability manifest | Suite adversaria + trazas |

> Añade los tuyos. Un RNF sin columna "cómo se mide" no es un requisito, es una intención.

## 3. Vista de arquitectura

### 3.1 Diagrama de contexto (C4 nivel 1)

> Quién habla con el sistema y con qué sistemas externos habla él. Mermaid o imagen exportada.

```mermaid
flowchart LR
    U[Usuario objetivo] --> S[Tu sistema]
    S --> LLM[Proveedor LLM]
    S --> EXT[APIs externas de las herramientas]
```

### 3.2 Diagrama de contenedores (C4 nivel 2)

> El diagrama central del documento. Cada caja debe existir: nada de componentes aspiracionales.
> Dibuja fronteras de confianza, harness, loop y capacidades; añade retrieval o grafos solo cuando
> formen parte del sistema real.

```mermaid
flowchart TB
    subgraph cloud [Plataforma: nómbrala]
        FE[Interfaz] --> API[Boundary de entrada]
        API --> H[Harness: contexto + policy]
        H --> LOOP[Loop: estado + budgets]
        LOOP --> RET[Retrieval opcional]
        RET --> VDB[(Vector DB: nómbrala)]
        LOOP --> CAP[Capabilities / executors]
    end
    ING[Pipeline de ingestión - job offline] --> VDB
    H -.-> OBS[Traces + evals]
    LOOP -.-> OBS
```

### 3.3 Flujo de una petición

> Diagrama de secuencia de la query típica, con latencias reales medidas por tramo una vez tengas el sistema (v1: estimadas; versión final: medidas). Este diagrama es el que usarás para justificar dónde ataca cada optimización de latencia.

```mermaid
sequenceDiagram
    participant U as Usuario
    participant A as API
    participant H as Harness
    participant G as Loop
    participant R as Retrieval
    participant L as LLM
    U->>A: pregunta
    A->>H: contexto + identidad + policy
    H->>G: inicia estado y presupuestos
    G->>L: decide herramienta (~X ms)
    G->>R: retrieve top-k (~X ms)
    R-->>G: chunks + metadatos
    G->>L: genera respuesta (~X ms)
    G-->>H: terminal + respuesta + evidencia
    H-->>A: salida validada
    A-->>U: streaming
```

## 4. Stack tecnológico y justificación

> Tabla de componentes elegidos. La columna clave es la última: la alternativa que perdió. Si para alguna fila no puedes nombrar una alternativa seria, o bien no investigaste, o bien la decisión era trivial y no merece fila.

| Capa | Elección | Por qué (1 línea) | Alternativa descartada → ADR |
|---|---|---|---|
| LLM generación | | | `adr/ADR-001.md` |
| Embeddings | | | |
| Vector DB | | | |
| Orquestación agente | | | |
| API / backend | | | |
| Plataforma cloud | | | |
| Observabilidad | | | |

## 5. Decisiones de arquitectura (índice de ADRs)

> Mínimo 5 ADRs para el proyecto de campo. Candidatos que casi siempre merecen uno: elección de vector DB, estrategia de chunking, modelo(s) de LLM y política de enrutado barato/caro, arquitectura del agente (por qué grafo y no cadena), plataforma de despliegue, y qué haces cuando el retrieval no encuentra nada.

| ID | Título | Estado |
|---|---|---|
| `ADR-001` | | aceptado |
| `ADR-002` | | aceptado |
| ADR-NNN | Decisión pendiente de registrar | Propietario y fecha objetivo |

## 6. Datos

> Origen del corpus, licencia/legalidad, volumen (documentos, chunks, tokens totales), pipeline de ingestión (pasos, idempotencia, cómo se re-indexa), y esquema de metadatos de cada chunk. Incluye qué PII contiene el corpus y qué haces al respecto (aunque la respuesta sea "ninguna, porque X").

## 7. Seguridad

> Los cinco mínimos, con una frase cada uno sobre tu implementación concreta: (1) gestión de secretos, (2) prompt injection — qué entra del usuario y del corpus al prompt y qué mitigas, (3) sandboxing/permisos de cada herramienta del agente, (4) rate limiting y auth de la API pública, (5) qué registras en trazas y si contiene datos de usuario.

## 8. Escalabilidad y límites conocidos

> Sé honesto: dónde se rompe el sistema primero al crecer (¿la vector DB? ¿el rate limit del proveedor LLM? ¿el coste?). Conecta con la [proyección de costes](../07-analisis-de-costes.md). Un "límites conocidos" sólido da más puntos en la defensa que fingir que escala infinito.

## 9. Registro de cambios del documento

| Versión | Fecha | Cambio |
|---|---|---|
| v1.0 | | Hipótesis iniciales antes de optimizar |
| v2.0 | | Revisión con el sistema ya medido |

> Conserva al menos dos snapshots: uno con las estimaciones iniciales y otro con números medidos y los
> ADRs que hayan cambiado de estado. El diff es una prueba de aprendizaje: qué creías, qué observaste
> y qué decisión cambió.
