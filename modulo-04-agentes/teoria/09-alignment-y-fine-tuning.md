# 09 — Alignment y fine-tuning: SFT, RLHF, RLAIF y Constitutional AI

> Tema conceptual. El objetivo es entender de dónde sale el comportamiento de los modelos y
> cuándo adaptar uno; no entrenaremos un foundation model en este programa.

Un modelo preentrenado predice el siguiente token. Para convertirlo en asistente se adapta su
comportamiento: seguir instrucciones, usar tools, rechazar ciertas solicitudes y producir formatos
útiles. **Alignment** nombra el problema amplio de orientar el sistema hacia intenciones y valores
humanos; fine-tuning es una familia de técnicas, no una garantía de alignment.

## 1. El pipeline mental

```text
pretraining masivo
      ↓
instruction tuning / SFT
      ↓
preferencias (RLHF, RLAIF, DPO y variantes)
      ↓
evaluación de capacidad + seguridad
      ↓
controles del sistema desplegado
```

Cada capa conserva fallos de la anterior y puede introducir otros. Un modelo alineado en promedio
no conoce permisos de tu aplicación ni sustituye guardrails de runtime.

## 2. Supervised fine-tuning (SFT)

SFT entrena con pares de instrucción-respuesta considerados deseables. Es útil para:

- estilo y formato repetible;
- terminología de dominio;
- patrones de tool calling;
- tareas estrechas con ejemplos de alta calidad;
- modelos pequeños especializados.

El objetivo típico minimiza cross-entropy sobre los tokens de la respuesta. La calidad del dataset
domina: ejemplos contradictorios o respuestas largas sin necesidad enseñan exactamente esos vicios.

Un dataset serio incluye positivos, abstenciones, límites, errores de tools y casos difíciles. No
solo caminos felices.

## 3. Reward model y RLHF

Flujo clásico:

1. Para un prompt se generan varias respuestas.
2. Anotadores humanos las ordenan o comparan.
3. Se entrena un **reward model** para predecir preferencia.
4. Una política se optimiza contra esa recompensa, históricamente con PPO y una penalización KL
   para no alejarse demasiado del modelo de referencia.

Intuición simplificada:

```text
reward_total = reward_preferencia - beta * divergencia_KL(politica, referencia)
```

Riesgos:

- el reward model hereda preferencias y sesgos de anotadores;
- *reward hacking*: la política explota atajos que suben score sin cumplir intención;
- respuestas complacientes o excesivamente seguras;
- reducción de diversidad;
- coste y complejidad operativa altos.

RLHF alinea con una distribución de feedback, no con una definición universal de verdad.

## 4. RLAIF y Constitutional AI

**RLAIF** sustituye o complementa parte del feedback humano con evaluaciones generadas por otro
modelo. Escala más y permite criterios explícitos, pero hereda errores del juez y puede amplificar
preferencias de su familia.

**Constitutional AI** propone principios escritos —una "constitución"— para criticar y revisar
respuestas, generar preferencias y entrenar una política más útil e inocua. Su valor conceptual es
hacer parte de los criterios explícitos y auditables.

No basta con redactar una constitución en el system prompt: el método incluye generación de
críticas/revisiones y aprendizaje de preferencias. En una app, una lista de políticas sigue siendo
útil, pero es control de prompting/runtime, no el entrenamiento descrito en el paper.

## 5. DPO y optimización directa de preferencias

**Direct Preference Optimization (DPO)** aprende directamente de tríos
`(prompt, respuesta_preferida, respuesta_rechazada)` sin entrenar y optimizar un reward model por
separado. Simplifica el pipeline y se ha convertido en referencia para adaptación por preferencias.

Variantes posteriores ajustan robustez, longitud, ruido de etiquetas o naturaleza online/offline.
La pregunta de ingeniería no es memorizar siglas: es qué datos tienes, qué comportamiento buscas,
qué capacidad de evaluación posees y cuánto drift toleras.

## 6. PEFT y LoRA

El fine-tuning completo actualiza todos los pesos y exige mucha memoria. **Parameter-Efficient
Fine-Tuning** entrena una fracción. LoRA congela el modelo base e introduce matrices de bajo rango:

```text
W_adaptada = W_base + escala * (A · B)
```

Ventajas:

- menos memoria y almacenamiento;
- adaptadores por tarea sobre un mismo modelo;
- entrenamiento accesible con hardware menor;
- rollback sencillo al retirar el adaptador.

Limitaciones: no crea conocimiento fiable de datos cambiantes, puede degradar capacidades y sigue
necesitando licencia compatible, evaluación y serving de la combinación correcta.

## 7. Fine-tuning frente a prompting, RAG y tools

| Necesidad | Primera opción |
|---|---|
| información privada o cambiante | RAG / consulta a fuente |
| formato fijo | structured outputs |
| regla de negocio exacta | código / tool |
| estilo y comportamiento repetido | prompt; SFT si escala y eval lo justifican |
| reducir coste con modelo pequeño | distillation/SFT con benchmark |
| enseñar vocabulario estable | RAG o SFT según tarea y volumen |
| corregir hechos concretos | fuente de verdad, no pesos |

Fine-tuning no es una base de datos. Actualizar una política mañana no debería requerir entrenar.

## 8. Tool use y alignment

Los modelos aprenden formatos de tools y patrones de decisión durante SFT/preference tuning. Pero
el contrato final lo define tu aplicación. Debes probar:

- cuándo llama y cuándo responde directamente;
- argumentos válidos y corrección tras error;
- obediencia a resultados negativos;
- resistencia a tools o documentos maliciosos;
- confirmación antes de efectos;
- parada y presupuesto.

Un modelo mejor entrenado reduce errores; no convierte un tool `execute_any_sql` en segura.

## 9. Dataset de adaptación

Buenas prácticas:

1. deduplicar y separar train/validation/test por fuente o entidad para evitar leakage;
2. conservar un test congelado que nunca entra en entrenamiento;
3. documentar licencia, consentimiento, procedencia y PII;
4. equilibrar tipos de tarea y casos de abstención;
5. incluir negativos y errores corregidos;
6. medir calidad de anotación y desacuerdo;
7. versionar dataset, código, base model, tokenizer y configuración.

Datos sintéticos ayudan a ampliar cobertura, pero no deben ser la única verdad: un modelo que
entrena y evalúa sus propios patrones puede crear una burbuja de auto-confirmación.

## 10. Evaluación antes y después

Compara el adaptado con el base en:

- tarea objetivo por segmentos;
- capacidades generales que no quieres perder;
- safety y prompt injection;
- calibración/abstención;
- formato y tool calling;
- latencia, throughput y coste;
- memorization y fuga de datos.

Haz ablation: prompt mejorado con modelo base, RAG sin fine-tuning, adaptador y combinación. Si el
prompt ya resuelve el problema, el entrenamiento añade mantenimiento sin valor.

## 11. Alignment del sistema, no solo del modelo

La unidad desplegada incluye modelo, prompt, retrieval, tools, permisos, UI, monitorización y
humanos. Controles fuertes:

- autorización y mínimo privilegio fuera del modelo;
- confirmación de efectos y transacciones idempotentes;
- fuentes con procedencia;
- validación de entradas/salidas;
- observabilidad y respuesta a incidentes;
- canales de apelación/corrección;
- evaluación continua tras cada cambio.

Un modelo no puede garantizar objetivos que no observa. Si no recibe identidad, permisos o estado
real, no puede respetarlos de forma fiable.

## Errores comunes

1. Fine-tunear para añadir documentación que cambia cada semana.
2. Entrenar antes de construir un baseline y una eval.
3. Usar test cases dentro de datos sintéticos de entrenamiento.
4. Confundir rechazo frecuente con seguridad completa.
5. Elegir una técnica por popularidad sin considerar datos y serving.
6. No medir regresiones fuera de la tarea objetivo.
7. Pensar que alignment del modelo reemplaza permisos del sistema.

## Para profundizar

- Ouyang et al. (2022), *Training language models to follow instructions with human feedback*:
  https://arxiv.org/abs/2203.02155
- Bai et al. (2022), *Constitutional AI*: https://arxiv.org/abs/2212.08073
- Rafailov et al. (2023), *Direct Preference Optimization*: https://arxiv.org/abs/2305.18290
- Hu et al. (2021), *LoRA*: https://arxiv.org/abs/2106.09685
- NIST AI RMF: https://www.nist.gov/itl/ai-risk-management-framework
