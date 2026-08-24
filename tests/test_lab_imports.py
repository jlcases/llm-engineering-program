from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
LABS = sorted(
    path
    for path in ROOT.glob("modulo-*/labs/*.py")
    if not path.name.startswith("_")
)


@pytest.mark.parametrize("path", LABS, ids=lambda path: str(path.relative_to(ROOT)))
def test_every_public_python_lab_imports_without_side_effects(path: Path) -> None:
    """A clean, fully synced environment must be able to load every advertised lab."""

    name = "llmec_smoke_" + "_".join(path.relative_to(ROOT).with_suffix("").parts).replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
        sys.modules.pop(name, None)


def test_lab_inventory_is_explicit_and_does_not_shrink_silently() -> None:
    assert len(LABS) == 39
