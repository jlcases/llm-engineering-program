"""Utilidades pequeñas compartidas por los labs del módulo 2."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = Path(__file__).resolve().parent / "data"
OUTPUTS_DIR = REPO_ROOT / "outputs"
load_dotenv(REPO_ROOT / ".env")

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5")


def require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        print(
            f"Falta {name}. Copia setup/.env.example a {REPO_ROOT / '.env'} y configúrala.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return value


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, payload: Any) -> None:
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
