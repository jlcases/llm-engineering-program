# 07 — Responsible AI: de principios a controles medibles

Responsible AI no es una página de valores ni un filtro al final. Es un proceso para identificar
quién puede sufrir daño, traducirlo a requisitos verificables y mantener evidencia durante todo el
ciclo de vida.

## 1. Del principio al control

| Principio | Pregunta operacional | Evidencia |
|---|---|---|
| Fairness | ¿qué grupos reciben resultados distintos y por qué? | métricas segmentadas, pares contrafactuales |
| Transparencia | ¿sabe el usuario que interactúa con IA y sus límites? | UI, model/system card |
| Explicabilidad | ¿podemos justificar datos, reglas y fuentes? | citas, features, trazas, reason codes |
| Privacidad | ¿qué datos entran, se guardan y se comparten? | inventario, DPIA, retención, borrado |
| Seguridad | ¿cómo se abusa o se extraen datos? | threat model, red-team, incidentes |
| Robustez | ¿qué ocurre fuera de distribución o al fallar tools? | evals, fault injection, SLOs |
| Accountability | ¿quién aprueba, monitoriza y responde? | RACI, gates, runbooks, logs |

Un principio sin propietario, métrica y gate no cambia decisiones de ingeniería.

## 2. Clasificar el caso por impacto

Antes del modelo documenta:

- usuarios y no usuarios afectados;
- decisiones que informa o automatiza;
- reversibilidad y gravedad del error;
- poblaciones vulnerables y contextos de uso no previstos;
- fuentes de datos y jurisdicciones;
- dependencia humana y posibilidad real de apelación;
- amenazas de abuso.

Cuanto mayor el impacto, más estrictos deben ser evidencia, supervisión y límites. Un generador de
copys internos y un sistema que prioriza solicitudes de ayuda no comparten umbral.

## 3. Human-in-the-loop que sí significa algo

Poner un botón "aprobar" no reduce riesgo si el humano:

- recibe cientos de casos por hora;
- no ve fuentes ni incertidumbre;
- cree que el modelo casi siempre acierta;
- es penalizado por discrepar;
- no puede editar ni revertir;
- no tiene formación ni autoridad.

Diseña la revisión con información, tiempo, reason codes, fuentes, edición y canal de escalado.
Mide override rate, precisión de overrides, tiempo y desacuerdo. Si nadie rechaza nunca, puede ser
calidad alta o automatización complaciente: investiga.

## 4. Fairness en sistemas generativos

Define grupos y resultado relevante. Para clasificación con ground truth puedes medir:

```text
TPR_g = verdaderos_positivos_g / positivos_reales_g
FPR_g = falsos_positivos_g / negativos_reales_g
gap_TPR = max(TPR_g) - min(TPR_g)
```

Para generación evalúa propiedades como toxicidad, estereotipos, calidad, rechazo, factualidad y
utilidad por segmento. Usa pares contrafactuales donde solo cambia el atributo, más casos naturales
que representen dialectos y situaciones reales.

Precauciones:

- tamaños de muestra pequeños producen gaps inestables;
- una media puede esconder intersecciones;
- remover una columna sensible no elimina proxies;
- distintas métricas de fairness pueden ser incompatibles;
- medir un atributo sensible requiere base legal, minimización y controles.

La definición justa pertenece al contexto del producto y debe involucrar a expertos y afectados.

## 5. Transparencia y explicabilidad

La explicación adecuada depende del consumidor:

- **usuario:** qué hace el sistema, qué datos usó, limitaciones y cómo corregir/apelar;
- **operaciones:** trace, fuentes, versión y eventos;
- **auditor:** controles, dataset, resultados y cambios;
- **ingeniería:** señales por componente y reproducción.

No presentes el chain-of-thought generado como explicación causal. Puede ser racionalización.
Prefiere evidencia verificable: reglas aplicadas, tool calls, citas y factores de decisión externos.

## 6. Model card y system card

Una ficha mínima:

```markdown
# Sistema: NebulaOps Support Assistant

## Propósito y fuera de alcance
- Ayuda a localizar documentación interna de soporte.
- No ejecuta cambios de infraestructura ni da asesoramiento legal.

## Componentes y versiones
- Modelo/política de routing
- Corpus e índice
- Prompts, tools y guardrails

## Datos
- Fuentes, licencias, actualización, PII y retención

## Evaluación
- Dataset, segmentos, métricas, intervalos y fallos conocidos

## Riesgos y mitigaciones
- Alucinación, sesgo, inyección, acceso cruzado y abuso

## Operación
- Propietario, alertas, rollback, feedback y contacto
```

Actualízala con cada cambio material; una ficha estática de lanzamiento se vuelve falsa.

## 7. Privacidad por diseño

Mapa de datos por etapa:

```text
entrada → logs/trazas → proveedor → retrieval/store → feedback/eval → backups → borrado
```

Para cada flecha responde finalidad, base, región, acceso, retención y eliminación. Controles:

- minimización y redacción antes de logging;
- separación de payload y metadata;
- opciones de no-retención y contratos del proveedor cuando corresponda;
- cifrado y acceso auditado;
- datasets de eval anonimizados;
- borrado propagado a índices, caches y backups según política;
- no reutilizar conversaciones para entrenamiento sin decisión explícita.

## 8. Evaluación con personas

Diseña una guía de anotación con ejemplos frontera. Usa al menos dos anotadores en una muestra y
mide acuerdo. El desacuerdo revela ambigüedad de política o tarea; no lo ocultes tomando una media.

Protege a anotadores de contenido dañino, informa sobre la tarea y evita recopilar atributos
personales irrelevantes. Responsible AI también aplica al proceso de evaluación.

## 9. Herramientas AWS relevantes

- **Amazon Bedrock Guardrails:** políticas configurables para entradas/salidas; mide falsos
  positivos y negativos sobre tu dominio.
- **Bedrock model evaluation:** evaluación automática o con humanos según capacidades vigentes.
- **SageMaker Clarify:** análisis de sesgo y explicabilidad para workflows de ML compatibles.
- **SageMaker Model Cards:** documentación y gobierno del ciclo de vida.
- **Amazon Macie:** descubrimiento de datos sensibles en S3, no filtro semántico universal.
- **CloudTrail/Config/Audit Manager:** evidencia de actividad, configuración y compliance.

Ningún servicio decide qué es justo para tu producto. Aporta mecanismos, no la definición.

## 10. Monitorización y cambio

Señales online:

- calidad por segmento y tasa de abstención;
- quejas, overrides y apelaciones;
- toxicidad/rechazo por idioma;
- drift de input y corpus;
- citas inválidas y acceso denegado;
- incidentes y near misses;
- coste/latencia que empuja a usuarios a atajos.

Define triggers de reevaluación: nuevo modelo, prompt, corpus, tool, mercado, idioma o política.

## 11. Governance ligera pero real

Para un equipo pequeño basta un registro versionado:

| Campo | Ejemplo |
|---|---|
| sistema/owner | support-assistant / equipo AI |
| nivel de impacto | medio |
| usos permitidos | búsqueda y borrador |
| usos prohibidos | decisión automática sobre personas |
| evaluaciones obligatorias | calidad, PII, injection, fairness por idioma |
| aprobadores | producto, seguridad, dominio |
| próxima revisión | fecha o trigger |
| rollback | alias/modelo/índice anterior |

La documentación debe reflejar decisiones, no producir burocracia sin control.

## Errores comunes

1. Tratar Responsible AI como sinónimo de moderación.
2. Medir fairness sin definir resultado o daño.
3. Llamar human-in-the-loop a una aprobación automática de facto.
4. Guardar todas las trazas "por si acaso".
5. Presentar texto generado por el modelo como explicación fiable.
6. No reevaluar tras cambiar corpus o modelo.
7. Delegar responsabilidad en el proveedor cloud.

## Para profundizar

- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
- OECD AI Principles: https://oecd.ai/en/ai-principles
- AWS Responsible AI: https://aws.amazon.com/machine-learning/responsible-ai/
- Model Cards: https://arxiv.org/abs/1810.03993
- Datasheets for Datasets: https://arxiv.org/abs/1803.09010
