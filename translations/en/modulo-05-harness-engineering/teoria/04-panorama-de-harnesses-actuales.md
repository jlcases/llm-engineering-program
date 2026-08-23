# 04 — Current landscape: compare architectures, not brands

A feature list expires; an architectural reading lets you understand the next product that appears.
This unit uses fifteen systems reviewed on August 23, 2026 to teach you how to locate who owns the
loop, where context comes from, where authority is enforced, and what kind of result can be
attributed to the harness.

The selection is a reference set chosen for architectural diversity, not a census or ranking. The
absence of a product implies no quality judgment. The structured catalog and its sources are in
[`harness_landscape.json`](../labs/data/harness_landscape.json).

## 1. Five layers commonly called a “harness”

| Layer | What it owns | Engineering question | Catalog examples |
|---|---|---|---|
| **Coding agent runtime** | One agent's loop, repository context, tools, and session | How does it turn model decisions into verifiable changes? | dsh, OpenCode, Goose, Crush, Aider, Claude Code, Pi, echoVic's Orca |
| **Personal agent runtime** | Persistent memory, skills, channels, and subagents | What does it learn across sessions, and what must it forget? | Hermes Agent, OpenHarness/Ohmo |
| **Integrated agent product** | Runtime plus IDE context, CLI, and approval UX | Which advantage comes from the editor and which from the loop? | Kilo Code, Cline, Continue |
| **Multi-agent ADE** | Processes, worktrees, and supervision for multiple agents | How does it isolate, compare, and merge candidates? | stablyai's Orca |
| **Workflow orchestrator** | Deterministic stages that delegate agentic turns | Which control is expressed in code instead of requested from the model? | VirtusLab's Orca |

The layer is not a score. An orchestrator is not “more advanced” than a runtime: it solves a
different problem. You may attribute a difference to the harness mechanism only when both
candidates occupy the same layer, receive the same surface, and work under equivalent contracts.

## 2. Fifteen systems, fifteen useful questions

| System | Architectural property that matters | Worthwhile experiment |
|---|---|---|
| **DeepSeek Harness (`dsh`)** | Adapter, tools, log, sandbox, and even the agent loop are plugins | Replace only the loop and measure recovery without changing model or authority |
| **OpenCode** | Coding runtime with terminal, desktop, IDE, and headless surfaces | Fix one surface and put context and compaction under pressure |
| **Goose** | General-purpose agent extended through MCP, not restricted to code | Compare a minimum and full manifest with the same model |
| **Crush** | Native TUI with sessions and compatible endpoints | Separate process overhead from loop quality |
| **Aider** | The model emits textual edit protocols, not the same tool-calling mechanics | Use it as a baseline for models that fail structured calls |
| **Hermes Agent** | Memory, skills, and subagents survive an isolated task | Measure legitimate transfer on a second pass without leaking the answer |
| **Claude Code** | Reference runtime with a demanding capability surface | Measure schema pressure and recovery without assuming undocumented compatibility |
| **Pi** | Extensible runtime with four default tools and no built-in permissions | Isolate it externally and sweep tool-surface size |
| **Orca — stablyai** | Coordinates existing agents in parallel worktrees | Measure best-of-N, duplicated cost, contamination, and merge load |
| **Orca — VirtusLab** | Typed, deterministic, resumable staged workflows | Assign a runtime/model per role and measure the composed system |
| **Orca — echoVic** | Third-party Rust coding agent with resumable sessions | Verify whether its specific defaults help under a fixed endpoint and sandbox |
| **OpenHarness/Ohmo** | Tools, skills, memory, and coordination infrastructure plus a reference agent | Separate framework value from Ohmo's behavior |
| **Kilo Code** | One product across VS Code, JetBrains, and CLI | Compare IDE and CLI while controlling diagnostics and ambient context |
| **Cline** | Shared engine across IDE, CLI, and SDK with human approval | Keep the same approval regime across every trial |
| **Continue** | Combines agent workflows with editor assistance and autocomplete | Evaluate each workload separately, never with one score |

The catalog's final columns separate verified facts from hypotheses. “It has memory” may be a design
fact. “Memory improves the result” remains a hypothesis until an experiment controls contamination,
the first pass, and the second.

## 3. The Orca case: one name, three identities

Treating “Orca” as one tool destroys any comparison:

1. [stablyai/orca](https://github.com/stablyai/orca) is an agent development environment. It launches
   other coding agents and separates their Git state through worktrees. The loop still belongs to
   Codex, Claude Code, OpenCode, Pi, or another delegated process.
2. [VirtusLab/orca](https://github.com/VirtusLab/orca) expresses development workflows as Scala
   stages. Stages are resumable, while planning, implementation, and review roles delegate to
   configurable agent backends.
3. [echoVic/orca-agent](https://github.com/echoVic/orca-agent) is a terminal coding agent. It is a
   third-party project; “DeepSeek-native” does not mean it belongs to DeepSeek.

Therefore, Pi versus stablyai's Orca does not answer “which harness is better.” Valid comparisons
are Pi versus another runtime under the same task contract, or Pi inside Orca versus Pi without that
orchestration to measure isolation and overhead. Lab 03 rejects the first question and accepts the
second as a composition test.

## 4. Five design theses that can be tested

### Deep replaceability

The official `dsh` architecture makes the model adapter, tool registry, session log, and loop
plugins. It also derives model-visible history from a durable event stream. This creates a valuable
experimental seam: modifying a loop without forking the rest of the product. The tradeoff is that
the effective configuration, not the binary's name, defines the harness that actually ran.

### Minimum surface

Pi provides `read`, `write`, `edit`, and `bash` by default, allows the selection to change, and keeps
compaction, tools, and extensions open. This austerity reduces initial schemas but does not create a
security boundary: its own documentation says the process inherits access to filesystem, network,
credentials, and processes. Prompt minimalism and least privilege are different properties.

### Text protocol as a baseline

Aider maintains explicit edit-format families such as whole file, search/replace blocks, and unified
diff. You must not score a response as a “failed tool call” when it never used that protocol. You can
compare the outcome of the same repair, but the conclusion applies to the complete system and must
retain tokens, application attempts, and patch conflicts.

### Persistence as an experimental treatment

Hermes and OpenHarness include memory or learning that exceeds one run. To measure it, the control
condition must execute two sessions without memory and the treated condition two sessions under a
declared retention policy. The second task must be analogous, not identical; otherwise the test
measures solution memorization. Memory entries belong to the auditable dataset.

### Orchestration above the loop

stablyai's Orca proposes parallel candidates in worktrees; VirtusLab's turns planning,
implementation, and review into deterministic, resumable stages. Neither magically improves a
model call. They may improve the outcome through selection, specialization, or recovery while
paying more compute, coordination, and effect surface. Those costs belong in the result.

## 5. Ambient context is also a variable

An IDE may provide open files, selection, LSP diagnostics, and editor state that a TUI cannot see. A
persistent app may remember conversations that a headless CLI does not receive. An ADE may offer
five candidates while the baseline runs only one.

Before comparing, record:

- exact surface: CLI, TUI, IDE, app, API, or headless;
- initial context and discovery rules;
- visible tools, complete schemas, and approval policy;
- filesystem, worktree, variables, credentials, and network policy;
- memory, caches, history, and state that cross session boundaries;
- who compacts, when, and what evidence is discarded;
- human process: extra prompts, approvals, selection, and merge.

If you cannot equalize a variable, do not hide the difference. Declare it as a confounder and limit
the claim to “this complete system obtained this outcome under these conditions.”

## 6. Security: where marketing ends

A worktree separates Git branches and directories; by itself it does not separate network, keychain,
processes, environment variables, or shared services. An approval dialog may improve supervision;
it does not replace permission checks in the executor. A compatible endpoint may accept messages;
it does not prove equivalent tool, streaming, cache, or error semantics to the original provider.

For harness adoption, trace at least these boundaries:

1. which code is installed and which installation scripts execute;
2. where sessions, prompts, traces, memory, and credentials persist;
3. which telemetry or external network is used in minimum configuration;
4. which identity creates processes and accesses the filesystem;
5. which actions bypass approval and who can change that policy;
6. how a session is revoked, state is cleaned, and cleanup is proven.

“Open source,” “local,” and “sandboxed” answer different questions. Verify all three separately.

## 7. How to keep the landscape alive

An acceptable catalog update needs a primary source, review date, and concrete architectural
difference. Do not accept a card copied from a landing page or a performance claim without trials.

The pull request must:

- link the official repository and documentation;
- assign a layer, cohort, and composition seam;
- separate verifiable facts from benchmark hypotheses;
- declare surface, loop, protocol, portability, and trust boundary;
- add a case that breaks if namesake products are merged;
- avoid stars, maturity adjectives, and ephemeral models as quality evidence.

Codex CLI, Gemini CLI, Qwen Code, and new runtimes are obvious candidates for expanding the set, but
they must pass through the same process. SOTA does not mean pretending to be exhaustive: it means
the method detects a new architecture, updates the evidence, and does not preserve stale claims as
truth.

## Primary sources for this reading

- [DeepSeek Harness — architecture](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.md)
- [Pi Agent Harness — packages, permissions, and isolation](https://github.com/earendil-works/pi)
- [Aider — edit formats](https://aider.chat/docs/more/edit-formats.html)
- [Hermes Agent](https://github.com/NousResearch/hermes-agent)
- [OpenHarness](https://github.com/HKUDS/OpenHarness)
- [stablyai's Orca](https://github.com/stablyai/orca)
- [VirtusLab's Orca](https://github.com/VirtusLab/orca)
- [echoVic's Orca Agent](https://github.com/echoVic/orca-agent)
- [OpenCode](https://github.com/anomalyco/opencode)
- [Goose](https://github.com/aaif-goose/goose)
- [Crush](https://github.com/charmbracelet/crush)
- [Claude Code](https://github.com/anthropics/claude-code)
- [Kilo Code](https://github.com/Kilo-Org/kilocode)
- [Cline](https://github.com/cline/cline)
- [Continue](https://github.com/continuedev/continue)
