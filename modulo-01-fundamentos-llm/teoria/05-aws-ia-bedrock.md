# Servicios de IA en AWS: Bedrock, SageMaker JumpStart y Amazon Q

> **Módulo 1 · Tema 5** · Tiempo estimado de estudio: 2,5 h
> Lab asociado: `labs/05_bedrock_inference.py`
> Ejercicios asociados: 8 y 10.

---

## 1. El mapa de la IA generativa en AWS

AWS no tiene "un" servicio de IA: tiene una pila de tres niveles, y elegir el nivel
correcto es la primera decisión de arquitectura:

```
┌──────────────────────────────────────────────────────────────┐
│  APLICACIONES        Amazon Q  (asistentes listos para usar) │
├──────────────────────────────────────────────────────────────┤
│  PLATAFORMA LLM      Amazon Bedrock  (modelos via API,       │
│                      serverless: sin gestionar GPUs)         │
├──────────────────────────────────────────────────────────────┤
│  INFRAESTRUCTURA ML  SageMaker (+ JumpStart)                 │
│                      (entrenar, ajustar y servir TUS         │
│                      modelos en TUS instancias)              │
└──────────────────────────────────────────────────────────────┘
```

**Analogía inmobiliaria.** Amazon Q es un hotel (todo hecho, poca personalización).
Bedrock es un piso de alquiler amueblado (traes tu ropa —prompts y datos—, no te ocupas
de la caldera). SageMaker es comprar un solar y construir (control total, y tuyo es
también el mantenimiento).

### Amazon Q — el nivel de aplicación

Asistentes empaquetados: **Q Business** (chat sobre los datos de la empresa, con
conectores a S3, SharePoint, Confluence...) y **Q Developer** (asistente de código,
sucesor de CodeWhisperer, integrado en IDEs y en la consola AWS). Se configuran, no se
programan. Útil saber que existen; poco que aprender aquí para un ingeniero LLM.

### SageMaker JumpStart — el nivel de infraestructura

SageMaker es la plataforma ML generalista (notebooks, entrenamiento, endpoints).
**JumpStart** es su catálogo de modelos preentrenados (Llama, Mistral, Falcon,
embeddings...) desplegables con un clic o unas líneas de SDK **en instancias GPU que tú
eliges y pagas por horas**. Lo usas cuando necesitas: pesos abiertos con control total,
fine-tuning propio, o un modelo que Bedrock no ofrece. A cambio: gestionas capacidad,
escalado y coste fijo por instancia encendida.

### Bedrock — el nivel de plataforma (el que nos importa)

API serverless para **foundation models de múltiples proveedores**. Pagas por token,
no gestionas infraestructura, y todo pasa por IAM y las cuentas de AWS. El resto del
tema es Bedrock, porque es la vía típica por la que una empresa "ya en AWS" consume LLMs.

---

## 2. Bedrock: conceptos fundamentales

### 2.1 Foundation models multi-proveedor

Bedrock ofrece bajo una única API modelos de: **Anthropic** (Claude), **Meta** (Llama),
**Mistral**, **Amazon** (la familia propia **Nova**, incluida Nova 2 Lite, y variantes
multimodales), Cohere, AI21, Stability, DeepSeek y otros. La propuesta de valor:

- **Una factura y un control de acceso** (IAM) para todos los modelos.
- **Los datos no salen de tu perímetro AWS** (región elegida, PrivateLink posible,
  y AWS se compromete a no usar tus prompts para entrenar).
- **Cambiar de modelo = cambiar un string**, no reescribir la integración (gracias a
  la Converse API, §3.2).

Cada modelo tiene un **model ID**. Ejemplos verificados en agosto de 2026:
`amazon.nova-2-lite-v1:0` y `eu.anthropic.claude-haiku-4-5-20251001-v1:0`.
El catálogo cambia y no todos los IDs están disponibles en todas las regiones.

### 2.2 Habilitación de acceso y regiones

Dos particularidades que te encontrarás el primer día:

1. **Model access.** Antes de invocar un modelo hay que habilitarlo en la consola
   (*Bedrock → Model access*). Hasta entonces, la API devuelve `AccessDeniedException`
   aunque tu IAM sea correcto.
2. **Regiones e inference profiles.** No todos los modelos están en todas las regiones.
   Además, los modelos recientes suelen exigir invocarse mediante **cross-region
   inference profiles**: IDs con prefijo de geografía (`us.`, `eu.`) que enrutan la
   petición entre varias regiones para absorber picos, p. ej.
   `eu.anthropic.claude-haiku-4-5-20251001-v1:0`. Si un model ID "normal" te da un error
   diciendo que uses un inference profile, es esto.

### 2.3 Modalidades de inferencia y precios

- **On-demand**: pago por token, sin compromiso. El modo por defecto y el del lab.
- **Batch**: trabajos asíncronos sobre ficheros en S3, con descuento, para volumen no
  interactivo.
- **Provisioned throughput**: capacidad reservada (por unidades de modelo) para cargas
  sostenidas con SLA de rendimiento; necesario también para servir modelos con
  fine-tuning propio.

Precios concretos: siempre en https://aws.amazon.com/bedrock/pricing/ (varían por
modelo, región y modalidad; no los memorices ni los cablees en código).

### 2.4 El ecosistema alrededor

Para tener el vocabulario (se ven en módulos posteriores): **Knowledge Bases** (RAG
gestionado sobre tus datos), **Agents** (orquestación de herramientas), **Guardrails**
(filtros de contenido y PII configurables), **Model evaluation**, y fine-tuning
gestionado de algunos modelos.

---

## 3. La API de Bedrock con boto3

Bedrock se divide en **dos clientes** de boto3, y confundirlos es el error nº 1:

```python
import boto3

bedrock = boto3.client("bedrock", region_name="eu-west-1")          # plano de CONTROL
runtime = boto3.client("bedrock-runtime", region_name="eu-west-1")  # plano de DATOS
```

- `bedrock`: gestión — listar modelos (`list_foundation_models`), fine-tuning, etc.
- `bedrock-runtime`: inferencia — aquí viven `invoke_model` y `converse`.

### 3.1 La vía antigua: `invoke_model`

Recibe un `body` JSON **con el formato nativo de cada proveedor**: el de Anthropic
(`anthropic_version`, `messages`...) no se parece al de Llama ni al de Titan/Nova.
Cambiar de modelo implicaba reescribir el payload y el parseo. La verás en código
legacy y la necesitarás para modelos no conversacionales (embeddings, imágenes).

### 3.2 La vía moderna: la Converse API

`converse` define **un formato único de mensajes para todos los modelos de texto**:

```python
response = runtime.converse(
    modelId="eu.anthropic.claude-haiku-4-5-20251001-v1:0",
    system=[{"text": "Eres un asistente conciso que responde en español."}],
    messages=[
        {"role": "user", "content": [{"text": "¿Qué es Amazon Bedrock?"}]}
    ],
    inferenceConfig={"maxTokens": 500, "temperature": 0.3, "topP": 0.9},
)

texto = response["output"]["message"]["content"][0]["text"]
uso   = response["usage"]          # inputTokens, outputTokens, totalTokens
parada = response["stopReason"]    # "end_turn", "max_tokens", ...
```

Observa el paralelismo con lo ya aprendido: `system` + lista de `messages` con roles
(como OpenAI/Anthropic), `inferenceConfig` con los parámetros del tema 3 (nombres en
camelCase), `usage` para contar tokens y `stopReason` para comprobar truncamientos.
La diferencia estructural: `content` es siempre una **lista de bloques** tipados
(`{"text": ...}`, imágenes, documentos, tool calls), igual que en la API nativa de
Anthropic. Existe `converse_stream` para streaming, y la Converse API soporta también
function calling (`toolConfig`) de forma uniforme entre modelos.

**Regla práctica: usa Converse siempre que el modelo la soporte** (todos los de chat
actuales). Es lo que hace el lab `05_bedrock_inference.py`.

### 3.3 Autenticación e IAM

boto3 resuelve credenciales por la cadena estándar: variables de entorno
(`AWS_ACCESS_KEY_ID`...), perfiles de `~/.aws/credentials` (`AWS_PROFILE`), roles de
instancia/SSO. Permisos mínimos para inferencia:

```json
{ "Effect": "Allow",
  "Action": ["bedrock:InvokeModel", "bedrock:InvokeModelWithResponseStream"],
  "Resource": "arn:aws:bedrock:*::foundation-model/*" }
```

En producción se restringe el `Resource` a los modelos concretos aprobados: es el
mecanismo real con el que una organización gobierna "quién puede usar qué modelo".

---

## 4. ¿Bedrock o la API directa del proveedor?

La misma familia Claude puede consumirse vía API de Anthropic o vía Bedrock. Criterios:

| Factor | API directa del proveedor | Bedrock |
|---|---|---|
| Novedades | Modelos y features el día del lanzamiento | Suelen llegar con retraso |
| Facturación | Tarjeta/contrato por proveedor | Factura AWS unificada (+ créditos, + Marketplace) |
| Compliance | Depende del proveedor | Perímetro AWS: IAM, CloudTrail, PrivateLink, regiones UE |
| Multi-modelo | Una integración por proveedor | Una API para todos (Converse) |
| Features avanzadas | Todas (p. ej. prompt caching completo) | Subconjunto según modelo |

Patrón habitual: prototipar con APIs directas (mejor DX, novedades antes) y desplegar
en Bedrock cuando la organización exige gobernanza AWS. Si diseñas bien la capa de
acceso al modelo (una función tuya que encapsula la llamada), migrar es barato.

---

## 5. Errores comunes

1. **Usar el cliente `bedrock` para inferir** (o `bedrock-runtime` para listar modelos).
   `UnknownOperationException` o método inexistente: revisa qué cliente creas.
2. **No habilitar el modelo en Model access** → `AccessDeniedException` con IAM
   perfecto. Se habilita por región: hacerlo en `us-east-1` no vale para `eu-west-1`.
3. **Región equivocada o model ID sin inference profile.** `ValidationException` o
   "model not found": comprueba disponibilidad por región y si el modelo exige prefijo
   `us.`/`eu.`.
4. **Payloads de `invoke_model` copiados entre proveedores.** Cada uno tiene su formato
   nativo; si mezclas, error de deserialización. Con Converse desaparece el problema.
5. **Ignorar `stopReason`/`usage`**: mismas consecuencias que ignorar `finish_reason`
   en OpenAI — respuestas truncadas y costes sin control.
6. **Credenciales AWS en el código.** Nunca: variables de entorno, perfiles o roles.
   (Y recuerda: las claves de OpenAI/Anthropic tampoco — `.env` fuera de git.)
7. **Montar SageMaker para algo que Bedrock ya sirve.** Empieza por el nivel más alto
   de la pila que cubra tu caso; baja solo cuando tengas una razón concreta.

---

## 6. Para profundizar

- **Documentación de Amazon Bedrock**: https://docs.aws.amazon.com/bedrock/
- **Referencia de la Converse API**:
  https://docs.aws.amazon.com/bedrock/latest/userguide/conversation-inference.html
- **boto3, cliente bedrock-runtime**:
  https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html
- **IDs de modelos e inference profiles soportados**:
  https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html
- **Pricing de Bedrock** (consultar siempre aquí, no memorizar):
  https://aws.amazon.com/bedrock/pricing/
- **SageMaker JumpStart**:
  https://docs.aws.amazon.com/sagemaker/latest/dg/studio-jumpstart.html
- **Amazon Q**: https://aws.amazon.com/q/
- **Claude en Bedrock (docs de Anthropic)**:
  https://docs.anthropic.com/en/api/claude-on-amazon-bedrock
