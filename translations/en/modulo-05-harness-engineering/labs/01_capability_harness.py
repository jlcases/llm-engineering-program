"""Lab 01 — Harness with a capability manifest, approval, sandbox, and traces.

Run:
    python modulo-05-harness-engineering/labs/01_capability_harness.py
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from _harness_core import AgentHarness, Capability, WorkspaceSandbox


def build_harness(root: Path, *, approve_writes: bool = False) -> AgentHarness:
    sandbox = WorkspaceSandbox(root)

    def read_file(arguments: dict[str, object]) -> dict[str, object]:
        path = str(arguments.get("path", ""))
        content = sandbox.read_text(path)
        return {"path": path, "content": content}

    def write_file(arguments: dict[str, object]) -> dict[str, object]:
        path = str(arguments.get("path", ""))
        content = str(arguments.get("content", ""))
        return sandbox.write_text(path, content)

    capabilities = [
        Capability(
            name="read_file",
            description="Read one UTF-8 file inside the task workspace.",
            input_schema={"type": "object", "required": ["path"]},
            handler=read_file,
        ),
        Capability(
            name="write_file",
            description="Write one UTF-8 file inside the task workspace.",
            input_schema={"type": "object", "required": ["path", "content"]},
            handler=write_file,
            effect="workspace_write",
            requires_approval=True,
        ),
    ]
    return AgentHarness(
        run_id="harness-demo-01",
        capabilities=capabilities,
        allowed={"read_file", "write_file"},
        approved={"write_file"} if approve_writes else set(),
    )


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="llmec-harness-") as temporary:
        root = Path(temporary)
        (root / "brief.md").write_text("Build an observable model router.\n", encoding="utf-8")
        harness = build_harness(root, approve_writes=True)

        brief = harness.invoke("read_file", {"path": "brief.md", "token": "never-log-me"})
        harness.invoke("write_file", {"path": "artifacts/decision.json", "content": json.dumps(brief)})

        print(json.dumps({"manifest": harness.manifest()}, ensure_ascii=False, indent=2))
        print(harness.trace.as_json())


if __name__ == "__main__":
    main()
