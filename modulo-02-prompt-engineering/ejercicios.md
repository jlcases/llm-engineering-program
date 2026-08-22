# Ejercicios — Módulo II

Los ejercicios están pensados para producir artefactos reutilizables. Guarda prompts, datasets y
resultados con versión. No optimices contra los ejemplos visibles hasta memorizar el test.

## 1. Zero-shot con contrato

Diseña un prompt para extraer de emails: intención (`cancelar`, `cambiar`, `consultar`, `otro`),
identificador opcional y urgencia. Define entrada, salida, criterios y abstención. Crea 12 casos,
incluidos 3 ambiguos, y mide exactitud por campo antes de añadir ejemplos.

## 2. Selección de few-shots

Elige cuatro ejemplos para el ejercicio 1. Justifica cobertura, diversidad y orden. Compara:

- ejemplos fijos;
- ejemplos seleccionados por similitud;
- un ejemplo por clase.

Evalúa sobre los mismos casos y registra tokens extra.

## 3. Self-consistency con presupuesto

Amplía el lab 02 a 20 problemas con respuesta verificable. Compara 1, 3, 5 y 9 muestras. Reporta
accuracy, acuerdo, tokens y coste. Decide el menor número de muestras que supera tu gate.

## 4. Jerarquía y contenido hostil

Construye 15 inputs donde el texto delimitado intenta cambiar rol, formato o revelar instrucciones.
Compara un system prompt ingenuo con otro que define fronteras y abstención. No llames "seguro" al
segundo: reporta tasa de ataque, falsos positivos y fallos restantes.

## 5. Tool loop en OpenAI

Añade al lab 03 una tool de historial de pagos y otra de creación de disputa. La escritura debe:

- requerir confirmación explícita ligada a factura e importe;
- usar una idempotency key;
- validar estado y permiso en código;
- simular respuesta perdida tras crear la disputa sin duplicarla al reintentar.

## 6. Portar tool use a Anthropic

Implementa las mismas tools del ejercicio 5 con Messages API. Documenta las diferencias entre
`function_call_output` y `tool_result`, llamadas paralelas, argumentos y señal de parada. Añade un
test donde una tool devuelve error.

## 7. Contrato Pydantic con reglas cruzadas

Extrae una reserva con `start_date`, `end_date`, asistentes y evidencia literal. Valida que fin sea
posterior a inicio, que asistentes no tenga duplicados y que cada campo opcional permita `null`.
Compara `.responses.parse` e Instructor ante tres inputs incompletos.

## 8. Golden dataset

Amplía `prompt_eval_cases.json` a 60 casos sin duplicados superficiales. Incluye segmentos, casos
críticos, dialectos y entradas fuera de alcance. Define guía de anotación y haz que otra persona
anote 15 casos; registra desacuerdos y resuélvelos antes de evaluar.

## 9. PromptSpec versionado

Implementa el `PromptSpec` del tema 06 con:

- hash SHA-256 del paquete;
- validación de variables;
- schema version;
- serialización JSON sin secretos;
- changelog y compatibilidad.

Escribe tests de variable ausente/sobrante y de hash estable.

## 10. Gate en CI

Convierte el lab 06 en dos jobs:

1. offline y sin secretos en todo PR;
2. evaluación live autorizada con límite de coste.

El gate debe bloquear regresión global > 2 puntos, recall crítico < 95 %, cualquier formato inválido
y coste estimado sobre presupuesto. Guarda resultados como artefacto.

## 11. Pares contrafactuales

Crea 30 pares donde solo cambia nombre percibido, variante regional o edad. Evalúa label, prioridad,
tono y longitud. Randomiza orden y repite tres veces. Reporta gap con intervalo y revisa manualmente
todos los pares discordantes.

## 12. Mini-proyecto — pipeline de evaluación de prompts

Elige una tarea real y entrega:

```text
proyecto-prompt/
├── prompts/               # baseline y candidata con metadata
├── schemas/               # contratos Pydantic/JSON Schema
├── data/                  # train/dev/test separados
├── evaluate.py            # métricas programáticas + judge calibrado
├── compare.py             # comparación pareada e intervalos
├── tests/                 # sin red
├── results/               # un run reproducible
└── README.md              # hipótesis, coste, riesgos y decisión
```

Gates mínimos:

- al menos 50 casos y 5 segmentos;
- esquema válido ≥ 99 %;
- métrica primaria y segmento crítico definidos antes del run;
- comparación pareada, no dos medias sin correspondencia;
- coste/tokens/latencia medidos;
- análisis de cinco fallos concretos;
- rollback por versión.

La entrega no se aprueba por "candidate gana": se aprueba si la decisión está sustentada y el
pipeline detectaría una regresión real.
