# Exercises — Harness Engineering

These exercises evaluate boundaries and evidence. A screenshot of final text without the trace and
environment state is not accepted as proof.

## 1. Minimum capability manifest

Define three capabilities for a repository-review agent: reading, running tests, and creating a
review comment. Include schema, effect, permissions, timeout, and errors.

**Acceptance criteria:**

- the manifest is validatable, versioned JSON;
- a read-only task does not discover the comment capability;
- additional arguments are rejected;
- every error declares whether it is retryable;
- a test proves that renaming a capability breaks the contract visibly.

## 2. Path traversal and symlinks

Extend lab 01 to permit an artifacts subdirectory and reject every escape, including a symlink
created inside the workspace that points outside it.

**Required cases:**

1. permitted relative path;
2. rejected `../`;
3. rejected absolute path;
4. rejected outward symlink;
5. internal symlink permitted only when policy declares it.

## 3. Single-use approval token

Implement approval for a tool with an external effect. Approval must bind the run, capability,
argument hash, and expiration.

**Acceptance criteria:**

- changing an argument invalidates the token;
- reusing it fails;
- an expired token never calls the executor;
- the log retains ID and decision, never the token;
- cancelling the run invalidates pending approvals.

## 4. Structural redaction

Create a policy that redacts secrets by field name and sensitive type, including inside nested lists.
Do not alter innocent data containing the word `token` in free text.

Deliver a corpus with positive and negative cases and measure false positives and false negatives.
Explain which data you prohibit entirely instead of attempting to redact it.

## 5. Contamination between trials

Deliberately introduce a shared cache that makes the second trial pass. Write a test detecting the
inflation and repair the runner through namespaces or cleanup.

**Evidence must include:**

- contaminated result;
- observable cause;
- isolated result;
- additional isolation cost;
- decision about which caches may be shared safely.

## 6. Graders in disagreement

Evaluate ten outputs with a deterministic rule, a model judge, and a small human rubric. Do not try
to force agreement: locate the dimension each grader interprets differently.

Report a disagreement matrix, three samples, and an adjudication policy. The final result must retain
every signal, not only a weighted average.

## 7. Harness failure

Make the fixture fail before the agent starts. The system must distinguish `infra_error` from
`agent_failure`, exclude it from the capability denominator, and keep it visible in harness
reliability.

Add timeout, grader exception, and cleanup failure as further routes.

## 8. Authority ADR

Write an ADR comparing:

- all tools always visible;
- progressive discovery;
- deterministic selection by task type.

Decide using token usage, correct-selection rate, latency, and authority surface. Include the
condition that would make you change alternatives.

## 9. Audit a current harness

Choose a runtime not yet in the catalog and prepare a contribution. Do not copy its feature list:
locate the loop, context assembly, interaction protocol, persistence, and the exact point where
permissions are enforced.

**Acceptance criteria:**

- primary repository and documentation with a review date;
- layer and cohort defended with evidence;
- facts separated from benchmark hypotheses;
- trust boundary covering installation, credentials, network, and persistent state;
- test that fails when an ID, repository, or source is duplicated;
- no popularity metric used as evidence of quality.

## 10. Invalid question

Extend lab 03 with a comparison requested by a product stakeholder that mixes an ADE and a coding
runtime. The program must reject direct causality and propose two alternative designs: a runtime
comparison or a composition treatment.

Add tests for a compatible cohort, incompatible layer, incomplete end-to-end controls, unknown
composition seam, and a verified one. The error message must explain which variable blocks the
claim rather than only returning `invalid`.

## 11. Mini benchmark edition

Turn one repair task into a six-fixture suite: two happy cases, two tool-failure cases, one with
context pressure, and one with denied permission. Run two candidates in alternating order with at
least three planned repetitions.

Deliver trial-level results, outcome rate by family, harness reliability, efficiency conditional on
success, intervals, and every infrastructure error. Explain which conclusion you still cannot
support even if one candidate ranks first.

## Submission

Publish code, happy/non-happy tests, an example manifest, two redacted traces, a trial report, and the
ADR. A reviewer must be able to reproduce everything without production credentials.
