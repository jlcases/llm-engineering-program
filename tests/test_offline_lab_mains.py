from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

OFFLINE_CASES = [
    ("modulo-01-fundamentos-llm/labs/01_primer_llamada_openai.py", ["--dry-run"]),
    ("modulo-01-fundamentos-llm/labs/02_primer_llamada_anthropic.py", ["--dry-run"]),
    ("modulo-01-fundamentos-llm/labs/03_tokenizacion_comparada.py", []),
    ("modulo-01-fundamentos-llm/labs/04_parametros_generacion.py", ["--dry-run"]),
    ("modulo-01-fundamentos-llm/labs/05_bedrock_inference.py", ["--dry-run"]),
    ("modulo-02-prompt-engineering/labs/01_zero_vs_few_shot.py", ["--dry-run"]),
    ("modulo-02-prompt-engineering/labs/02_chain_of_thought.py", ["--dry-run"]),
    ("modulo-02-prompt-engineering/labs/03_function_calling_openai.py", ["--dry-run"]),
    ("modulo-02-prompt-engineering/labs/04_tool_use_anthropic.py", ["--dry-run"]),
    ("modulo-02-prompt-engineering/labs/05_structured_outputs_instructor.py", ["--dry-run"]),
    ("modulo-02-prompt-engineering/labs/06_eval_prompts_dataset.py", ["--offline"]),
    ("modulo-03-rag/labs/01_embeddings_similitud.py", ["--lexical"]),
    ("modulo-03-rag/labs/02_rag_minimo.py", ["--lexical"]),
    ("modulo-03-rag/labs/03_chunking_comparado.py", ["--lexical", "--limit", "2"]),
    ("modulo-03-rag/labs/04_reranking.py", ["--lexical", "--limit", "2"]),
    ("modulo-03-rag/labs/05_rag_avanzado_multiquery_hyde.py", ["--lexical", "--offline"]),
    ("modulo-03-rag/labs/06_evaluacion_ragas.py", ["--offline", "--lexical", "--limit", "2", "--output", "{tmp}/rag.json"]),
    ("modulo-04-agentes/labs/01_react_desde_cero.py", []),
    ("modulo-04-agentes/labs/02_langgraph_basico.py", []),
    ("modulo-04-agentes/labs/03_langgraph_ciclos_condicionales.py", []),
    ("modulo-04-agentes/labs/04_langgraph_checkpoints.py", []),
    ("modulo-04-agentes/labs/06_multiagente_supervisor.py", []),
    ("modulo-04-agentes/labs/07_memoria_agente.py", ["--forget"]),
    ("modulo-05-harness-engineering/labs/01_capability_harness.py", []),
    ("modulo-05-harness-engineering/labs/02_eval_harness.py", []),
    ("modulo-05-harness-engineering/labs/03_harness_landscape.py", ["--list"]),
    ("modulo-06-loop-engineering/labs/01_bounded_loop.py", []),
    ("modulo-06-loop-engineering/labs/02_durable_loop.py", []),
    ("modulo-07-graph-engineering/labs/01_typed_provenance_graph.py", []),
    ("modulo-07-graph-engineering/labs/02_hybrid_graph_retrieval.py", []),
    ("modulo-08-production-engineering/labs/01_trazas_manuales.py", ["--output", "{tmp}/trace.jsonl"]),
    ("modulo-08-production-engineering/labs/02_langsmith_tracing.py", []),
    ("modulo-08-production-engineering/labs/03_cache_semantico.py", []),
    ("modulo-08-production-engineering/labs/04_model_routing.py", []),
    ("modulo-08-production-engineering/labs/05_eval_regresion.py", ["--output", "{tmp}/eval.json"]),
    ("modulo-08-production-engineering/labs/07_prompt_injection.py", []),
]


def load_module(relative_path: str):
    path = ROOT / relative_path
    name = "llmec_offline_" + "_".join(path.relative_to(ROOT).with_suffix("").parts).replace("-", "_")
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module, path


@pytest.mark.parametrize("relative_path,arguments", OFFLINE_CASES, ids=[case[0] for case in OFFLINE_CASES])
def test_offline_or_dry_run_happy_path(
    relative_path: str,
    arguments: list[str],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    module, path = load_module(relative_path)
    resolved_arguments = [argument.replace("{tmp}", str(tmp_path)) for argument in arguments]
    if hasattr(module, "OUTPUTS_DIR"):
        monkeypatch.setattr(module, "OUTPUTS_DIR", tmp_path)
    if hasattr(module, "RESULTS_DIR"):
        monkeypatch.setattr(module, "RESULTS_DIR", tmp_path)
    monkeypatch.setattr(sys, "argv", [str(path), *resolved_arguments])
    assert module.main() in (None, 0)


def test_offline_inventory_covers_every_safe_main() -> None:
    assert len(OFFLINE_CASES) == 36


@pytest.mark.parametrize(
    "relative_path,arguments,expected",
    [
        (
            "modulo-02-prompt-engineering/labs/06_eval_prompts_dataset.py",
            ["--offline", "--limit", "0"],
            SystemExit,
        ),
        (
            "modulo-03-rag/labs/04_reranking.py",
            ["--lexical", "--final-k", "0"],
            ValueError,
        ),
        (
            "modulo-04-agentes/labs/01_react_desde_cero.py",
            ["--max-steps", "0"],
            ValueError,
        ),
        (
            "modulo-08-production-engineering/labs/02_langsmith_tracing.py",
            ["--send"],
            RuntimeError,
        ),
    ],
)
def test_offline_cli_rejects_invalid_or_unauthorized_modes(
    relative_path: str,
    arguments: list[str],
    expected: type[BaseException],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    module, path = load_module(relative_path)
    monkeypatch.delenv("LANGSMITH_API_KEY", raising=False)
    monkeypatch.setattr(sys, "argv", [str(path), *arguments])
    with pytest.raises(expected):
        module.main()


def test_regression_lab_returns_nonzero_when_gate_fails(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    relative_path = "modulo-08-production-engineering/labs/05_eval_regresion.py"
    module, path = load_module(relative_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [str(path), "--simulate-regression", "--output", str(tmp_path / "failed.json")],
    )
    assert module.main() == 1
    assert (tmp_path / "failed.json").is_file()
