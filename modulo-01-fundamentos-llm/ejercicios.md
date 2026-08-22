# Ejercicios — Módulo I

Hazlos en orden. Los ejercicios 1–8 consolidan conceptos; 9–10 son el hito del módulo. Registra
mediciones y decisiones, no solo capturas de que un script terminó.

## 1. Atención a mano

Con una sola cabeza y dimensión 2:

```text
Q = [[1, 0], [0, 1]]
K = [[1, 0], [1, 1]]
V = [[2, 0], [0, 4]]
```

Calcula `softmax(QKᵀ / √2)V` para ambos tokens. Repite aplicando máscara causal al primer token.
Explica qué cambia y por qué.

**Criterio:** matrices intermedias, softmax por fila y resultado numérico aproximado.

## 2. Presupuesto de contexto

Con `o200k_base`, mide tokens de tres textos de al menos 1.000 caracteres: español, inglés y
código. Para una ventana hipotética de 32.000 tokens reserva 2.000 para salida y 1.500 para system,
tools y overhead. Calcula cuántos textos completos caben y documenta el margen real.

## 3. Truncado seguro

Implementa `truncate_to_tokens(text: str, limit: int, encoding_name: str) -> str`. Debe validar que
`limit >= 0`, nunca superar el límite al recodificar y manejar Unicode. Añade tests para vacío,
emoji, español y código.

## 4. Muestreo reproducible en términos estadísticos

Ejecuta el lab 04 cinco veces por temperatura. No compares igualdad exacta: define dos métricas de
diversidad (por ejemplo, ratio de tokens únicos y similitud Jaccard entre muestras) y representa la
distribución. Explica por qué `temperature=0` no es garantía criptográfica.

## 5. Truncado de salida

Fuerza `max_tokens`/límite de salida muy bajo en OpenAI y Anthropic. Detecta el motivo de parada y
devuelve un error de dominio `IncompleteGeneration` en vez de texto parcial. Decide cuándo tendría
sentido continuar y cuándo reiniciar.

## 6. Contrato común de proveedores

Define un `LLMResult` con texto, modelo real, input/output tokens, motivo de parada, latencia y
proveedor. Adapta labs 01–02 sin perder metadata. Escribe un test con clientes falsos.

## 7. Mini-evaluación de modelos

Crea 20 casos de una tarea concreta (clasificación, extracción o Q&A breve). Compara dos modelos
con el mismo prompt y parámetros razonables. Reporta métrica de calidad, formato inválido, p50/p95
de latencia y tokens. Elige el modelo más barato que supere tu umbral, sin usar rankings externos
como resultado.

## 8. Bedrock y mínimo privilegio

Escribe una política IAM para el lab 05 que solo permita `bedrock:InvokeModel` e
`bedrock:InvokeModelWithResponseStream` sobre el modelo/inference profile elegido. Explica qué
recurso y región debes adaptar. Ejecuta primero `--dry-run` y, si tienes cuenta, una llamada real.

## 9. Capacidad de contexto de una conversación

Implementa un contador que reciba mensajes y un presupuesto. Debe reservar salida, avisar al 80 %
y proponer qué turnos antiguos resumir sin eliminar system ni el último turno. Compara conteo exacto
para un proveedor con una estimación para otro y etiqueta claramente la incertidumbre.

## 10. Mini-proyecto — cliente multi-proveedor

Construye un CLI con interfaz común para OpenAI, Anthropic y Bedrock:

```bash
python cliente_multi_proveedor.py --provider openai --prompt "¿Qué es una KV cache?"
python cliente_multi_proveedor.py --provider anthropic --prompt "¿Qué es una KV cache?"
python cliente_multi_proveedor.py --provider bedrock --prompt "¿Qué es una KV cache?"
```

Requisitos:

- selección por CLI sin `if` repartidos por toda la aplicación;
- modelos configurables por entorno;
- `LLMResult` común y metadata visible;
- timeout/error traducido a mensajes útiles sin filtrar secretos;
- registro JSONL opcional con latencia/tokens, no el prompt por defecto;
- tests con fakes que no llaman a APIs;
- README con autenticación, coste y limitaciones.

**Superación:** las tres implementaciones cumplen el mismo contrato y una caída de un proveedor no
se confunde con una respuesta vacía.
