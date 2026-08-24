# Setup del entorno

## 1. Python y dependencias

Requiere Python ≥ 3.12 y [`uv`](https://docs.astral.sh/uv/).

```bash
cd llm-engineering-program
uv sync --locked --all-extras
source .venv/bin/activate
```

`uv sync --locked` instala únicamente la base de los módulos 1–2. Usa `--all-extras` para que los
labs de RAG, agentes, harnesses y producción no dependan de paquetes que casualmente ya estuvieran
en tu máquina.

Alternativa sin uv:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e '.[rag,agents,ops,dev]'
```

## 2. Claves API

Copia la plantilla y rellena solo las claves que vayas a usar en cada módulo:

```bash
cp setup/.env.example .env
```

| Variable | Dónde obtenerla | Se usa desde |
|---|---|---|
| `OPENAI_API_KEY` | platform.openai.com | Módulo 1 |
| `ANTHROPIC_API_KEY` | console.anthropic.com | Módulo 1 |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` / `AWS_REGION` | Consola AWS (IAM) | Módulo 1 (Bedrock) |
| `COHERE_API_KEY` | dashboard.cohere.com | Módulo 3 (rerank) |
| `LANGSMITH_API_KEY` | smith.langchain.com | Módulo 8 (solo con `--send`) |

Los labs cargan `.env` con `python-dotenv`. **Nunca** subas `.env` al repo (ya está en `.gitignore`).

## 3. Coste estimado de APIs

El coste depende del catálogo y la tarifa vigentes. Los ejemplos de agosto de 2026 usan
`gpt-5.6-luna` y `claude-haiku-4-5` para volumen, y reservan tiers superiores para
comparativas justificadas. Consulta el precio oficial antes de cada corrida y fija un
presupuesto; los módulos 3–5 incluyen además recorridos offline o modelos locales con Ollama.

## 4. Servicios locales opcionales

- **Ollama** (`brew install ollama`) — modelos locales para labs de despliegue y para trabajar sin coste de API.
- **Docker Desktop** — necesario en el módulo 8 (contenedores) y para Qdrant/pgvector locales en el módulo 3.
- **Node ≥ 20** — solo para el frontend Next.js del módulo 3.

## 5. Verificación

```bash
python setup/check_env.py --profile all
```

Comprueba la versión de Python y las dependencias del perfil elegido. Por seguridad, solo indica si
existe `.env`: nunca carga, inspecciona ni muestra el estado de credenciales concretas.

## 6. Compatibilidad de Instructor

El entorno principal fija el SDK actual de OpenAI 3.x. Instructor 1.15.4, la versión
vigente al 21-08-2026, declara `openai<3` y `rich<15`; instalarlo en el mismo entorno
haría el lock irresoluble. El lab de structured outputs usa la API nativa por defecto y
mantiene la comparación con Instructor en un proceso aislado:

```bash
uv run --no-project \
  --with-requirements setup/requirements-instructor.txt \
  python modulo-02-prompt-engineering/labs/05_structured_outputs_instructor.py \
  --backend instructor
```

Esto no cambia el modelo (`OPENAI_MODEL=gpt-5.6-luna`); aísla únicamente las versiones
de SDK incompatibles. El fichero de requisitos deja la decisión reproducible.

RAGAS 0.4.3 arrastra la misma dependencia. Además se fija `langchain-community<0.4`: RAGAS aún
importa `chat_models.vertexai`, módulo eliminado en la rama 0.4.x. Su modo live se ejecuta de forma
aislada y con retrieval lexical para no mezclar un segundo stack de embeddings:

```bash
uv run --no-project \
  --with-requirements setup/requirements-ragas.txt \
  python modulo-03-rag/labs/06_evaluacion_ragas.py \
  --ragas --lexical --limit 5
```

El modo `--offline` del lab pertenece al entorno principal y no necesita RAGAS ni claves.
