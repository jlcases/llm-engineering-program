from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path

import pytest
from jsonschema.exceptions import SchemaError

ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative_path: str):
    path = ROOT / relative_path
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    sys.path.insert(0, str(path.parent))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.remove(str(path.parent))
    return module


harness = load_module("llmec_security_harness", "modulo-05-harness-engineering/labs/_harness_core.py")
loop = load_module("llmec_security_loop", "modulo-06-loop-engineering/labs/_loop_core.py")
graph = load_module("llmec_security_graph", "modulo-07-graph-engineering/labs/_graph_core.py")
rag_common = load_module("llmec_rag_common", "modulo-03-rag/labs/_rag_common.py")
prompt_eval = load_module(
    "llmec_prompt_eval",
    "modulo-02-prompt-engineering/labs/06_eval_prompts_dataset.py",
)


def test_harness_enforces_json_schema_before_calling_handler() -> None:
    calls = []
    capability = harness.Capability(
        name="count",
        description="Count safely",
        input_schema={
            "type": "object",
            "properties": {"count": {"type": "integer"}},
            "required": ["count"],
            "additionalProperties": False,
        },
        handler=lambda arguments: calls.append(arguments) or {"ok": True},
    )
    runtime = harness.AgentHarness(run_id="schema", capabilities=[capability], allowed={"count"})
    with pytest.raises(ValueError, match="invalid arguments"):
        runtime.invoke("count", {"count": "not-an-integer"})
    assert calls == []
    assert runtime.trace.events[-1].payload == {
        "reason": "invalid_arguments",
        "path": "$['count']",
        "rule": "type",
    }


def test_harness_rejects_invalid_schema_at_startup() -> None:
    with pytest.raises(SchemaError):
        harness.Capability(
            name="broken",
            description="Invalid contract",
            input_schema={"type": "not-a-json-schema-type"},
            handler=lambda _: {},
        )


def test_harness_snapshots_schema_and_rejects_non_json_arguments() -> None:
    schema = {
        "type": "object",
        "properties": {"count": {"type": "integer"}},
        "required": ["count"],
    }
    calls = []
    capability = harness.Capability(
        name="snapshot",
        description="Immutable public contract",
        input_schema=schema,
        handler=lambda arguments: calls.append(arguments) or {"ok": True},
    )
    schema["required"] = []
    manifest = capability.public_contract()
    manifest["input_schema"]["required"] = []
    runtime = harness.AgentHarness(
        run_id="snapshot", capabilities=[capability], allowed={"snapshot"}
    )

    with pytest.raises(ValueError, match="invalid arguments"):
        runtime.invoke("snapshot", {})
    with pytest.raises(TypeError, match="JSON serializable"):
        runtime.invoke("snapshot", {"count": object()})
    assert calls == []


@pytest.mark.parametrize(
    "overrides,error",
    [
        ({"name": " "}, "name"),
        ({"description": ""}, "description"),
        ({"effect": ""}, "effect"),
        ({"requires_approval": 1}, "requires_approval"),
        ({"input_schema": []}, "input_schema"),
        ({"handler": None}, "handler"),
    ],
)
def test_harness_rejects_malformed_capability_contracts(overrides, error: str) -> None:
    values = {
        "name": "valid",
        "description": "Valid capability",
        "effect": "read",
        "requires_approval": False,
        "input_schema": {"type": "object"},
        "handler": lambda _: {},
    }
    values.update(overrides)
    with pytest.raises((TypeError, ValueError), match=error):
        harness.Capability(**values)


def test_harness_denies_unknown_disallowed_and_non_object_calls() -> None:
    capability = harness.Capability(
        name="known",
        description="Known capability",
        input_schema={"type": "object"},
        handler=lambda _: {},
    )
    runtime = harness.AgentHarness(run_id="denials", capabilities=[capability], allowed=set())
    with pytest.raises(KeyError, match="unknown"):
        runtime.invoke("missing", {})
    with pytest.raises(PermissionError, match="not allowed"):
        runtime.invoke("known", {})

    allowed = harness.AgentHarness(
        run_id="bad-arguments", capabilities=[capability], allowed={"known"}
    )
    with pytest.raises(TypeError, match="JSON object"):
        allowed.invoke("known", [])


def test_harness_redacts_nested_results_and_never_records_exception_messages() -> None:
    capability = harness.Capability(
        name="secret",
        description="Return nested credentials",
        input_schema={"type": "object"},
        handler=lambda _: {
            "nested": {"accessToken": "RESULT-CANARY"},
            "headers": {"X-API-Key": "API-CANARY"},
        },
    )
    runtime = harness.AgentHarness(run_id="redaction", capabilities=[capability], allowed={"secret"})
    runtime.invoke("secret", {})
    trace = runtime.trace.as_json()
    assert "RESULT-CANARY" not in trace
    assert "API-CANARY" not in trace
    assert trace.count("[REDACTED]") == 2

    failing = harness.Capability(
        name="fail",
        description="Raise a sensitive error",
        input_schema={"type": "object"},
        handler=lambda _: (_ for _ in ()).throw(RuntimeError("Bearer ERROR-CANARY")),
    )
    failed = harness.AgentHarness(run_id="failure", capabilities=[failing], allowed={"fail"})
    with pytest.raises(RuntimeError, match="ERROR-CANARY"):
        failed.invoke("fail", {})
    assert "ERROR-CANARY" not in failed.trace.as_json()
    assert failed.trace.events[-1].payload == {"error_type": "RuntimeError"}


def test_harness_rejects_non_mapping_and_unserializable_results() -> None:
    non_mapping = harness.Capability(
        name="list",
        description="Wrong return contract",
        input_schema={"type": "object"},
        handler=lambda _: ["wrong"],
    )
    runtime = harness.AgentHarness(run_id="bad-result", capabilities=[non_mapping], allowed={"list"})
    with pytest.raises(TypeError, match="must return a mapping"):
        runtime.invoke("list", {})

    cyclic = {}
    cyclic["self"] = cyclic
    invalid = harness.Capability(
        name="cyclic",
        description="Cyclic return value",
        input_schema={"type": "object"},
        handler=lambda _: cyclic,
    )
    runtime = harness.AgentHarness(run_id="cyclic", capabilities=[invalid], allowed={"cyclic"})
    with pytest.raises(TypeError, match="unserializable"):
        runtime.invoke("cyclic", {})

    object_result = harness.Capability(
        name="object",
        description="Non-JSON return value",
        input_schema={"type": "object"},
        handler=lambda _: {"value": object()},
    )
    runtime = harness.AgentHarness(
        run_id="object", capabilities=[object_result], allowed={"object"}
    )
    with pytest.raises(TypeError, match="unserializable"):
        runtime.invoke("object", {})


def test_loop_checkpoint_preserves_elapsed_budget() -> None:
    runtime = loop.DurableLoop(
        loop.LoopState(run_id="elapsed", task="wait"),
        loop.Budgets(max_elapsed_ms=1_000),
        started_ns=time.monotonic_ns() - 2_000_000_000,
    )
    assert runtime._budget_reason() == "time_budget"
    restored = loop.DurableLoop.restore(runtime.checkpoint())
    assert restored._budget_reason() == "time_budget"


def test_loop_rejects_negative_usage_and_corrupt_checkpoints() -> None:
    with pytest.raises(ValueError, match="tokens"):
        loop.ActionResult("bad", "bad", tokens=-1)
    with pytest.raises(ValueError, match="cost_micros"):
        loop.ActionResult("bad", "bad", cost_micros=-1)

    runtime = loop.DurableLoop(loop.LoopState(run_id="valid", task="task"), loop.Budgets())
    payload = json.loads(runtime.checkpoint())
    payload["state"]["usage"]["tokens"] = -1
    with pytest.raises(ValueError, match="tokens"):
        loop.DurableLoop.restore(json.dumps(payload))
    payload = json.loads(runtime.checkpoint())
    payload["unknown"] = True
    with pytest.raises(ValueError, match="missing or unknown"):
        loop.DurableLoop.restore(json.dumps(payload))


def test_loop_converts_planner_and_executor_failures_into_redacted_terminal_state() -> None:
    planner_failure = loop.DurableLoop(
        loop.LoopState(run_id="planner", task="task"), loop.Budgets()
    )
    status = planner_failure.step(
        lambda _: (_ for _ in ()).throw(RuntimeError("PLANNER-CANARY")),
        lambda *_: None,
    )
    assert status is loop.RunStatus.FAILED
    assert planner_failure.state.terminal_reason == "unhandled_planner_error"
    assert "PLANNER-CANARY" not in json.dumps(planner_failure.state.events)

    executor_failure = loop.DurableLoop(
        loop.LoopState(run_id="executor", task="task"), loop.Budgets()
    )
    status = executor_failure.step(
        lambda _: loop.Decision(kind="action", action="explode"),
        lambda *_: (_ for _ in ()).throw(RuntimeError("EXECUTOR-CANARY")),
    )
    assert status is loop.RunStatus.FAILED
    assert executor_failure.state.terminal_reason == "unhandled_action_error"
    assert "EXECUTOR-CANARY" not in json.dumps(executor_failure.state.events)


def test_loop_allows_exact_token_budget_then_final_answer() -> None:
    runtime = loop.DurableLoop(
        loop.LoopState(run_id="exact", task="task"),
        loop.Budgets(max_steps=2, max_tokens=10, max_cost_micros=20),
    )

    def planner(state):
        if state.observation:
            return loop.Decision(kind="final", answer="done")
        return loop.Decision(kind="action", action="work")

    result = runtime.run(
        planner,
        lambda *_: loop.ActionResult("complete", "complete", tokens=10, cost_micros=20),
    )
    assert result.status is loop.RunStatus.SUCCEEDED
    assert result.usage.tokens == 10
    assert result.usage.cost_micros == 20


@pytest.mark.parametrize(
    "usage,budgets,reason",
    [
        (loop.Usage(steps=1), loop.Budgets(max_steps=1), "step_budget"),
        (loop.Usage(tokens=2), loop.Budgets(max_tokens=1), "token_budget"),
        (loop.Usage(cost_micros=2), loop.Budgets(max_cost_micros=1), "cost_budget"),
        (loop.Usage(effects=2), loop.Budgets(max_effects=1), "effect_budget"),
    ],
)
def test_loop_reports_each_budget_dimension(usage, budgets, reason: str) -> None:
    runtime = loop.DurableLoop(loop.LoopState(run_id=reason, task="task", usage=usage), budgets)
    assert runtime._budget_reason() == reason
    assert runtime.step(lambda _: None, lambda *_: None) is loop.RunStatus.EXHAUSTED


@pytest.mark.parametrize(
    "decision,status,reason",
    [
        (loop.Decision(kind="final"), loop.RunStatus.FAILED, "empty_final_answer"),
        (loop.Decision(kind="impossible"), loop.RunStatus.FAILED, "task_impossible"),
        (
            loop.Decision(kind="human"),
            loop.RunStatus.NEEDS_HUMAN,
            "human_judgement_required",
        ),
        (loop.Decision(kind="unknown"), loop.RunStatus.FAILED, "invalid_decision"),
    ],
)
def test_loop_terminal_decision_contracts(decision, status, reason: str) -> None:
    runtime = loop.DurableLoop(loop.LoopState(run_id=reason, task="task"), loop.Budgets())
    assert runtime.step(lambda _: decision, lambda *_: None) is status
    assert runtime.state.terminal_reason == reason
    assert runtime.step(lambda _: None, lambda *_: None) is status


def test_loop_rejects_invalid_contract_objects_and_effect_over_budget() -> None:
    with pytest.raises(ValueError, match="max_elapsed_ms"):
        loop.Budgets(max_elapsed_ms=0)
    with pytest.raises(ValueError, match="max_steps"):
        loop.Budgets(max_steps=-1)
    with pytest.raises(TypeError, match="strings"):
        loop.ActionResult(1, "marker")
    with pytest.raises(TypeError, match="boolean"):
        loop.ActionResult("ok", "marker", effect_applied=1)
    with pytest.raises(TypeError, match="JSON serializable"):
        loop.Decision(kind="action", action="work", arguments={"bad": object()})
    with pytest.raises(TypeError, match="run_id"):
        loop.LoopState(run_id=1, task="task")
    with pytest.raises(ValueError, match="blank"):
        loop.LoopState(run_id=" ", task="task")
    with pytest.raises(TypeError, match="contract types"):
        loop.DurableLoop(object(), loop.Budgets())
    with pytest.raises(ValueError, match="started_ns"):
        loop.DurableLoop(
            loop.LoopState(run_id="future", task="task"),
            loop.Budgets(),
            started_ns=time.monotonic_ns() + 1_000_000,
        )

    invalid_decision = loop.DurableLoop(
        loop.LoopState(run_id="invalid-decision", task="task"), loop.Budgets()
    )
    assert invalid_decision.step(lambda _: {"kind": "final"}, lambda *_: None) is loop.RunStatus.FAILED

    wrong_executor = loop.DurableLoop(
        loop.LoopState(run_id="wrong-executor", task="task"), loop.Budgets()
    )
    assert wrong_executor.step(
        lambda _: loop.Decision(kind="action", action="work"), lambda *_: {"ok": True}
    ) is loop.RunStatus.FAILED

    no_effects = loop.DurableLoop(
        loop.LoopState(run_id="no-effects", task="task"), loop.Budgets(max_effects=0)
    )
    called = []
    assert no_effects.step(
        lambda _: loop.Decision(kind="action", action="send", effect_key="send:1"),
        lambda *_: called.append(True) or loop.ActionResult("sent", "sent", effect_applied=True),
    ) is loop.RunStatus.EXHAUSTED
    assert called == []


def test_loop_planner_cannot_mutate_durable_state_out_of_band() -> None:
    runtime = loop.DurableLoop(
        loop.LoopState(run_id="isolated", task="task"), loop.Budgets(max_tokens=10)
    )

    def planner(snapshot):
        snapshot.usage.tokens = 999
        snapshot.events.append({"kind": "forged"})
        return loop.Decision(kind="final", answer="done")

    assert runtime.step(planner, lambda *_: None) is loop.RunStatus.SUCCEEDED
    assert runtime.state.usage.tokens == 0
    assert all(event.get("kind") != "forged" for event in runtime.state.events)


def test_loop_restore_rejects_malformed_shapes_and_migrates_v1() -> None:
    runtime = loop.DurableLoop(loop.LoopState(run_id="restore", task="task"), loop.Budgets())
    payload = json.loads(runtime.checkpoint())

    with pytest.raises(TypeError, match="JSON object"):
        loop.DurableLoop.restore("[]")
    unsupported = dict(payload, checkpoint_version=999)
    with pytest.raises(ValueError, match="unsupported"):
        loop.DurableLoop.restore(json.dumps(unsupported))
    bad_state = dict(payload, state=[])
    with pytest.raises(TypeError, match="state and budgets"):
        loop.DurableLoop.restore(json.dumps(bad_state))
    bad_usage = json.loads(runtime.checkpoint())
    bad_usage["state"]["usage"] = []
    with pytest.raises(TypeError, match="usage"):
        loop.DurableLoop.restore(json.dumps(bad_usage))
    bad_cancel = json.loads(runtime.checkpoint())
    bad_cancel["state"]["cancel_requested"] = "false"
    with pytest.raises(TypeError, match="cancel_requested"):
        loop.DurableLoop.restore(json.dumps(bad_cancel))

    legacy = json.loads(runtime.checkpoint())
    legacy["checkpoint_version"] = 1
    legacy.pop("elapsed_ms")
    restored = loop.DurableLoop.restore(json.dumps(legacy))
    assert restored.state.run_id == "restore"
    assert restored._elapsed_ms() < 100


def test_graph_tokenization_preserves_unicode_words() -> None:
    assert graph.tokens("evaluación y producción") == {"evaluación", "y", "producción"}


def test_graph_contract_objects_reject_malformed_values() -> None:
    with pytest.raises(TypeError, match="text"):
        graph.tokens(1)
    with pytest.raises(ValueError, match="node_id"):
        graph.Node(" ", "service")
    with pytest.raises(ValueError, match="node_type"):
        graph.Node("node", " ")
    with pytest.raises(TypeError, match="properties"):
        graph.Node("node", "service", [])
    with pytest.raises(ValueError, match="source"):
        graph.Edge("", "uses", "target", ("doc:1",))
    with pytest.raises(TypeError, match="evidence_ids"):
        graph.Edge("source", "uses", "target", ["doc:1"])
    with pytest.raises(ValueError, match="blank"):
        graph.Edge("source", "uses", "target", ("",))
    with pytest.raises(ValueError, match="unique"):
        graph.Edge("source", "uses", "target", ("doc:1", "doc:1"))
    with pytest.raises(ValueError, match="evidence ID"):
        graph.EvidenceDocument(" ", "text", ())
    with pytest.raises(TypeError, match="text"):
        graph.EvidenceDocument("doc:1", 1, ())
    with pytest.raises(TypeError, match="entity_ids"):
        graph.EvidenceDocument("doc:1", "text", [])
    with pytest.raises(ValueError, match="entity IDs"):
        graph.EvidenceDocument("doc:1", "text", ("",))
    with pytest.raises(ValueError, match="unique"):
        graph.EvidenceDocument("doc:1", "text", ("node", "node"))

    network = graph.TypedGraph()
    with pytest.raises(TypeError, match="Node"):
        network.add_node(object())
    with pytest.raises(TypeError, match="Edge"):
        network.add_edge(object())
    with pytest.raises(TypeError, match="TypedGraph"):
        graph.HybridGraphRetriever(object(), [])
    with pytest.raises(TypeError, match="EvidenceDocument"):
        graph.HybridGraphRetriever(network, [object()])


def test_graph_rejects_duplicate_documents_and_invalid_limits() -> None:
    network = graph.TypedGraph()
    network.add_node(graph.Node("a", "service"))
    duplicate = [
        graph.EvidenceDocument("doc:1", "first", ("a",)),
        graph.EvidenceDocument("doc:1", "second", ("a",)),
    ]
    with pytest.raises(ValueError, match="unique"):
        graph.HybridGraphRetriever(network, duplicate)

    retriever = graph.HybridGraphRetriever(
        network, [graph.EvidenceDocument("doc:1", "evidence", ("a",))]
    )
    assert retriever.lexical("   ") == []
    with pytest.raises(ValueError, match="limit"):
        retriever.lexical("query", limit=0)
    with pytest.raises(ValueError, match="limit"):
        retriever.lexical("query", limit=True)
    assert retriever.lexical("no-overlap-token") == []
    with pytest.raises(ValueError, match="max_hops"):
        network.shortest_path("a", "a", max_hops=True)


def test_graph_provenance_requires_evidence_linked_to_both_endpoints() -> None:
    network = graph.TypedGraph()
    network.add_node(graph.Node("router", "service"))
    network.add_node(graph.Node("model", "model"))
    network.add_edge(graph.Edge("router", "uses", "model", ("doc:1",)))
    retriever = graph.HybridGraphRetriever(
        network,
        [graph.EvidenceDocument("doc:1", "router uses model", ("unrelated",))],
    )
    result = retriever.retrieve("router model", source_entity="router", target_entity="model")
    assert result.provenance_complete is False


def document(doc_id: str = "doc:1", text: str = "one two three"):
    return rag_common.Document(doc_id, "Title", text, f"{doc_id}.md", {})


def test_rag_contract_objects_reject_malformed_values() -> None:
    with pytest.raises(TypeError, match="title"):
        rag_common.Document("doc:1", 1, "text", "source.md", {})
    with pytest.raises(ValueError, match="doc_id"):
        rag_common.Document(" ", "Title", "text", "source.md", {})
    with pytest.raises(TypeError, match="metadata"):
        rag_common.Document("doc:1", "Title", "text", "source.md", {"page": 1})
    with pytest.raises(TypeError, match="chunk_id"):
        rag_common.Chunk(1, "doc:1", "Title", "text", "source.md", 0)
    with pytest.raises(ValueError, match="chunk_id"):
        rag_common.Chunk(" ", "doc:1", "Title", "text", "source.md", 0)
    with pytest.raises(ValueError, match="position"):
        rag_common.Chunk("chunk:1", "doc:1", "Title", "text", "source.md", True)


def test_rag_chunkers_validate_ids_limits_and_oversized_paragraphs() -> None:
    with pytest.raises(ValueError, match="duplicado"):
        rag_common.fixed_word_chunks([document(), document()])
    with pytest.raises(ValueError, match="max_words"):
        rag_common.heading_chunks([document()], max_words=0)
    chunks = rag_common.paragraph_chunks([document(text="one two three four five")], max_words=2)
    assert [len(chunk.text.split()) for chunk in chunks] == [2, 2, 1]
    assert len({chunk.chunk_id for chunk in chunks}) == 3


def test_rag_index_and_fusion_reject_ambiguous_inputs() -> None:
    chunks = rag_common.fixed_word_chunks([document()], size=2, overlap=0)
    index = rag_common.SearchIndex(chunks, lexical=True)
    with pytest.raises(ValueError, match="query"):
        index.search(" ")
    with pytest.raises(ValueError, match="top_k"):
        index.search("one", top_k=1.5)
    assert index.search("no-overlap-token") == []
    with pytest.raises(ValueError, match="k"):
        rag_common.reciprocal_rank_fusion([], k=-1)

    conflicting = rag_common.Chunk(
        chunks[0].chunk_id, "doc:2", "Other", "other", "other.md", 0
    )
    with pytest.raises(ValueError, match="conflictivo"):
        rag_common.reciprocal_rank_fusion(
            [
                [rag_common.SearchHit(chunks[0], 1.0)],
                [rag_common.SearchHit(conflicting, 1.0)],
            ]
        )


def test_prompt_eval_rejects_empty_summaries_and_non_positive_limits() -> None:
    with pytest.raises(ValueError, match="al menos un resultado"):
        prompt_eval.summarize([])
    with pytest.raises(argparse.ArgumentTypeError, match="mayor que cero"):
        prompt_eval.positive_int("0")
    assert prompt_eval.positive_int("3") == 3
