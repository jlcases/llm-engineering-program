"""Verifica Python, dependencias por perfil y claves API configuradas.

Uso: python setup/check_env.py --profile all
"""

import argparse
import importlib.util
import os
import sys
from pathlib import Path

OK, FAIL, WARN = "\033[92m✓\033[0m", "\033[91m✗\033[0m", "\033[93m~\033[0m"

PROFILE_PACKAGES = {
    "base": [
        "openai",
        "anthropic",
        "boto3",
        "tiktoken",
        "pydantic",
        "dotenv",
        "rich",
        "httpx",
        "jsonschema",
    ],
    "rag": ["numpy", "qdrant_client", "sentence_transformers", "cohere", "fastapi", "uvicorn", "pypdf"],
    "agents": ["langgraph", "mcp"],
    "ops": ["langsmith", "prometheus_client", "locust"],
}
API_KEYS = {
    "OPENAI_API_KEY": "OpenAI (módulo 1+)",
    "ANTHROPIC_API_KEY": "Anthropic (módulo 1+)",
    "AWS_ACCESS_KEY_ID": "AWS Bedrock (módulo 1+)",
    "COHERE_API_KEY": "Cohere rerank (módulo 3)",
    "LANGSMITH_API_KEY": "LangSmith (módulo 8, solo con --send)",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        choices=["base", "rag", "agents", "ops", "all"],
        default="all",
        help="Conjunto de dependencias que debe estar disponible (por defecto: all).",
    )
    return parser.parse_args()


def required_packages(profile: str) -> list[str]:
    selected = PROFILE_PACKAGES if profile == "all" else {"base": PROFILE_PACKAGES["base"], profile: PROFILE_PACKAGES[profile]}
    return list(dict.fromkeys(package for packages in selected.values() for package in packages))


def main() -> int:
    args = parse_args()
    errors = 0

    # Este script también se invoca directamente antes de crear el entorno del proyecto.
    if sys.version_info >= (3, 12):  # noqa: UP036
        print(f"{OK} Python {sys.version.split()[0]}")
    else:
        print(f"{FAIL} Python {sys.version.split()[0]} — se requiere >= 3.12")
        errors += 1

    for pkg in required_packages(args.profile):
        if importlib.util.find_spec(pkg):
            print(f"{OK} paquete {pkg}")
        else:
            print(f"{FAIL} falta el paquete {pkg} — ejecuta `uv sync --locked --all-extras`")
            errors += 1

    print(
        f"{WARN} Instructor y RAGAS se comprueban en sus entornos aislados "
        "(setup/requirements-*.txt)"
    )

    env_path = Path(__file__).resolve().parent.parent / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_path)
        except ImportError:
            pass
    else:
        print(f"{WARN} no hay .env en la raíz — copia setup/.env.example")

    for key, desc in API_KEYS.items():
        configured = bool(os.environ.get(key))
        icon = OK if configured else WARN
        state = "credencial configurada" if configured else "credencial sin configurar"
        print(f"{icon} {desc} — {state}")

    print("\nTodo listo." if errors == 0 else f"\n{errors} problema(s) bloqueante(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
