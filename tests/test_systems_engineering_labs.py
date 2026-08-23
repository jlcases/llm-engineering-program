from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


harness = load_module("llmec_harness_core", "modulo-05-harness-engineering/labs/_harness_core.py")
landscape = load_module(
    "llmec_landscape_core", "modulo-05-harness-engineering/labs/_landscape_core.py"
)
loop = load_module("llmec_loop_core", "modulo-06-loop-engineering/labs/_loop_core.py")
graph = load_module("llmec_graph_core", "modulo-07-graph-engineering/labs/_graph_core.py")

LANDSCAPE_PATH = (
    ROOT / "modulo-05-harness-engineering/labs/data/harness_landscape.json"
)


def test_harness_sandbox_blocks_escape_and_absolute_paths(tmp_path: Path) -> None:
    sandbox = harness.WorkspaceSandbox(tmp_path / "workspace")
    with pytest.raises(PermissionError, match="escapes"):
        sandbox.read_text("../secret.txt")
    with pytest.raises(PermissionError, match="absolute"):
        sandbox.read_text(str(tmp_path / "secret.txt"))


def test_harness_requires_approval_and_redacts_trace_secrets() -> None:
    called: list[dict[str, object]] = []
    capability = harness.Capability(
        name="publish",
        description="Publish an artifact",
        input_schema={"type": "object"},
        handler=lambda arguments: called.append(arguments) or {"ok": True},
        effect="external_write",
        requires_approval=True,
    )
    denied = harness.AgentHarness(run_id="denied", capabilities=[capability], allowed={"publish"})
    with pytest.raises(PermissionError, match="approval"):
        denied.invoke("publish", {"token": "sensitive"})
    assert called == []

    approved = harness.AgentHarness(
        run_id="approved",
        capabilities=[capability],
        allowed={"publish"},
        approved={"publish"},
    )
    assert approved.invoke("publish", {"token": "sensitive"}) == {"ok": True}
    assert "sensitive" not in approved.trace.as_json()
    assert "[REDACTED]" in approved.trace.as_json()


def test_harness_rejects_unknown_allowed_capability() -> None:
    with pytest.raises(ValueError, match="unknown allowed"):
        harness.AgentHarness(run_id="bad", capabilities=[], allowed={"shell"})


def test_harness_landscape_is_auditable_and_covers_the_local_reference_set() -> None:
    catalog = landscape.HarnessLandscape.from_path(LANDSCAPE_PATH)
    expected = {
        "deepseek-harness",
        "opencode",
        "goose",
        "crush",
        "aider",
        "hermes-agent",
        "claude-code",
        "pi",
        "orca-stablyai",
        "orca-virtuslab",
        "orca-echovic",
        "openharness",
        "kilo-code",
        "cline",
        "continue",
    }
    assert {record.id for record in catalog.records} == expected
    assert catalog.reviewed_at == "2026-08-23"
    assert all(record.primary_sources[0] == record.repository for record in catalog.records)
    assert all(record.verified_facts for record in catalog.records)
    assert all(record.benchmark_hypotheses for record in catalog.records)


def test_harness_landscape_keeps_the_three_orcas_architecturally_distinct() -> None:
    catalog = landscape.HarnessLandscape.from_path(LANDSCAPE_PATH)
    orcas = [
        catalog.get("orca-stablyai"),
        catalog.get("orca-virtuslab"),
        catalog.get("orca-echovic"),
    ]
    assert len({record.repository for record in orcas}) == 3
    assert {record.primary_layer for record in orcas} == {
        "multi_agent_ade",
        "workflow_orchestrator",
        "coding_agent_runtime",
    }


def test_harness_landscape_accepts_mechanism_and_composition_happy_paths() -> None:
    catalog = landscape.HarnessLandscape.from_path(LANDSCAPE_PATH)
    mechanism = catalog.compare("pi", "opencode", mode=landscape.MECHANISM_MODE)
    assert mechanism.claim_scope == "mechanism differences inside native_tool_cli"
    assert mechanism.confounders == ()

    composition = catalog.compare(
        "orca-stablyai", "pi", mode=landscape.COMPOSITION_MODE
    )
    assert composition.claim_scope == "composition contract and orchestration overhead"
    assert composition.confounders == ("composed_system",)


def test_harness_landscape_rejects_causally_invalid_comparisons() -> None:
    catalog = landscape.HarnessLandscape.from_path(LANDSCAPE_PATH)
    with pytest.raises(landscape.IncomparableHarnessError, match="same comparison cohort"):
        catalog.compare("pi", "orca-stablyai", mode=landscape.MECHANISM_MODE)
    with pytest.raises(landscape.IncomparableHarnessError, match="no verified composition seam"):
        catalog.compare("aider", "hermes-agent", mode=landscape.COMPOSITION_MODE)
    with pytest.raises(landscape.IncomparableHarnessError, match="two different systems"):
        catalog.compare("pi", "pi", mode=landscape.MECHANISM_MODE)


def test_harness_landscape_requires_controls_for_end_to_end_claims() -> None:
    catalog = landscape.HarnessLandscape.from_path(LANDSCAPE_PATH)
    with pytest.raises(landscape.IncomparableHarnessError, match="missing controls"):
        catalog.compare(
            "aider",
            "pi",
            mode=landscape.OUTCOME_MODE,
            controlled_variables={"model", "task_fixture"},
        )

    comparison = catalog.compare(
        "aider",
        "pi",
        mode=landscape.OUTCOME_MODE,
        controlled_variables=set(landscape.REQUIRED_OUTCOME_CONTROLS),
    )
    assert comparison.claim_scope == "end-to-end system outcome; no isolated harness causality"
    assert comparison.confounders == ("interaction_surface", "interaction_protocol")


def test_harness_landscape_rejects_missing_evidence_and_duplicate_repositories() -> None:
    payload = json.loads(LANDSCAPE_PATH.read_text(encoding="utf-8"))
    payload["harnesses"][0]["primarySources"] = []
    with pytest.raises(landscape.CatalogValidationError, match="primarySources"):
        landscape.HarnessLandscape(payload)

    payload = json.loads(LANDSCAPE_PATH.read_text(encoding="utf-8"))
    payload["harnesses"][1]["repository"] = payload["harnesses"][0]["repository"]
    payload["harnesses"][1]["primarySources"][0] = payload["harnesses"][0]["repository"]
    with pytest.raises(landscape.CatalogValidationError, match="duplicate repository"):
        landscape.HarnessLandscape(payload)


def test_loop_happy_path_reaches_explicit_success() -> None:
    runtime = loop.DurableLoop(loop.LoopState(run_id="ok", task="count"), loop.Budgets(max_steps=4))

    def planner(state):
        value = int(state.observation or "2")
        return loop.Decision(kind="final", answer="done") if value == 0 else loop.Decision(
            kind="action", action="decrement", arguments={"value": value}
        )

    def executor(_action, arguments):
        value = int(arguments["value"]) - 1
        return loop.ActionResult(str(value), f"remaining:{value}")

    result = runtime.run(planner, executor)
    assert result.status is loop.RunStatus.SUCCEEDED
    assert result.answer == "done"


def test_loop_non_happy_paths_cancel_stagnate_and_reject_unkeyed_effect() -> None:
    cancelled = loop.DurableLoop(loop.LoopState(run_id="cancel", task="x"), loop.Budgets())
    cancelled.request_cancel()
    assert cancelled.step(lambda _state: loop.Decision(kind="final", answer="late"), lambda *_: None) is loop.RunStatus.CANCELLED

    stagnant = loop.DurableLoop(
        loop.LoopState(run_id="stagnant", task="x"),
        loop.Budgets(max_steps=6, max_stagnant_steps=1),
    )
    stagnant_result = stagnant.run(
        lambda _state: loop.Decision(kind="action", action="observe"),
        lambda *_: loop.ActionResult("same", "same"),
    )
    assert stagnant_result.status is loop.RunStatus.EXHAUSTED
    assert stagnant_result.terminal_reason == "no_progress"

    unsafe = loop.DurableLoop(loop.LoopState(run_id="unsafe", task="x"), loop.Budgets())
    status = unsafe.step(
        lambda _state: loop.Decision(kind="action", action="send"),
        lambda *_: loop.ActionResult("sent", "sent", effect_applied=True),
    )
    assert status is loop.RunStatus.FAILED
    assert unsafe.state.terminal_reason == "effect_without_idempotency_key"


def test_loop_checkpoint_preserves_effect_receipt_and_prevents_replay() -> None:
    calls: list[str] = []
    runtime = loop.DurableLoop(loop.LoopState(run_id="durable", task="notify"), loop.Budgets(max_steps=4))

    def planner(state):
        if state.effect_receipts:
            return loop.Decision(kind="final", answer="done")
        return loop.Decision(kind="action", action="notify", effect_key="durable:notify")

    def executor(*_args):
        calls.append("notify")
        return loop.ActionResult("accepted", "accepted", effect_applied=True)

    runtime.step(planner, executor)
    restored = loop.DurableLoop.restore(runtime.checkpoint())
    restored.run(planner, executor)
    assert calls == ["notify"]
    assert restored.state.status is loop.RunStatus.SUCCEEDED


def test_graph_enforces_identity_endpoints_and_provenance() -> None:
    network = graph.TypedGraph()
    network.add_node(graph.Node("a", "service"))
    with pytest.raises(ValueError, match="conflicting"):
        network.add_node(graph.Node("a", "model"))
    with pytest.raises(ValueError, match="endpoints"):
        network.add_edge(graph.Edge("a", "uses", "missing", ("doc:1",)))
    network.add_node(graph.Node("b", "model"))
    with pytest.raises(ValueError, match="provenance"):
        network.add_edge(graph.Edge("a", "uses", "b", ()))


def test_hybrid_graph_retrieval_adds_multi_hop_evidence() -> None:
    network = graph.TypedGraph()
    for node_id, node_type in [("router", "service"), ("model", "model"), ("policy", "policy")]:
        network.add_node(graph.Node(node_id, node_type))
    network.add_edge(graph.Edge("router", "selects", "model", ("doc:1",)))
    network.add_edge(graph.Edge("model", "constrained_by", "policy", ("doc:2",)))
    retriever = graph.HybridGraphRetriever(
        network,
        [
            graph.EvidenceDocument("doc:1", "Router model selection", ("router", "model")),
            graph.EvidenceDocument("doc:2", "Latency policy", ("model", "policy")),
            graph.EvidenceDocument("doc:3", "Unrelated color palette", ("ui",)),
        ],
    )
    result = retriever.retrieve("router policy", source_entity="router", target_entity="policy")
    assert result.provenance_complete is True
    assert result.graph_paths == (("router", "selects", "model"), ("model", "constrained_by", "policy"))
    assert {"doc:1", "doc:2"}.issubset(result.evidence_ids)
