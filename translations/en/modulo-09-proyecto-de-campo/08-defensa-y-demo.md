# Demo and Technical Review Guide

The goal is not to show every screen, but to prove the chain problem → decision → behavior →
evidence → limit. Prepare a short version and a deep version; duration depends on the review context,
not an academic format. Rehearse it with a contingency plan that does not depend on improvisation.

## Reference script

| Minute | Content | Visible Evidence |
|---:|---|---|
| 0–2 | user, pain, scope, and non-goals | a sentence and a realistic case |
| 2–4 | architecture and two key decisions | diagram + ADRs |
| 4–7 | RAG/agent happy path | response, citations, and tool trace |
| 7–10 | difficult case/out-of-corpus | correct abstention or clarification |
| 10–12 | attack or tool error | control, degraded output, no side effect |
| 12–14 | approval/resumption | checkpoint and approval actor |
| 14–16 | eval and ablation | result per case, not just mean |
| 16–18 | production | dashboard, uptime, p95, and tested alert |
| 18–19 | cost | cost/task and 10× projection |
| 19–20 | limits and next decision | two prioritized known failures |

Do not write code live. Bring prepared queries in a versioned file and reset the state before the rehearsal. Teach at least one failure: a demo that only works does not demonstrate that the system knows how to fail.

## Contingency Plan

- recent video/screenshot of maximum three minutes for provider or cloud outage;
- results and dashboard exported with timestamp and commit;
- offline mode against fixtures to demonstrate graph, tools, and errors;
- second network and verified credentials without showing them;
- rollback command and previous version available;
- a slide declaring which part is live and which is recorded evidence.

Do not present an old recording as live. If something fails, open the trace, explain the limit, and use the fallback: diagnosing well during the demo adds more value than hiding the incident.

## Rehearsal Checklist

- two full rehearsals under 19 minutes;
- another person asks five unprepared questions;
- links, login, and monitoring tested from a clean profile/browser;
- demo data without PII and reversible side effects;
- caches warmed or declared; cold start measured;
- zoom/size legible and notifications silenced;
- final commit/digest annotated and feature freeze active.

## Review questions

Prepare answers with numbers and your own artifacts. “It’s a best practice” does not justify a decision.

### Problem and Architecture

1. Which specific user could not replace this with traditional search?
2. What part of the problem did you decide not to solve and why?
3. What is the first bottleneck at 10× scale and what metric demonstrates it?
4. Why an agent and not a deterministic chain?
5. What would you remove if you had to halve the complexity?
6. Which ADR changed most between the initial hypothesis and the measured version?
7. Which external dependency has the largest blast radius and how do you isolate it?

### RAG and Evaluation

8. How do you know the corpus contains the answer before blaming retrieval?
9. Why did you choose that chunking strategy and what ablation supports it?
10. What is the difference between retrieving the correct document and the correct chunk?
11. Where does your reranker fail and how much does it add to p95?
12. How does it behave when faced with a question outside the corpus?
13. Which five cases have the worst faithfulness and what is their root cause?
14. How much variance does your judge have and what did you manually audit?
15. What prevents a valid citation from supporting a false claim?
16. How do you invalidate the index when the parser, chunker, or embedding changes?

### Agent and Tools

17. What state and edge prevent an infinite loop?
18. What is the error contract for each tool?
19. How do you test idempotency when the response is lost after the commit?
20. Which actions require confirmation and to which arguments is it tied?
21. Can a retrieved document trigger a tool? What control prevents this?
22. Why does your multi-agent design improve upon the single-agent baseline?
23. How do you resume a task after a restart without repeating side effects?
24. What memory do you save, for how long, and how do you handle deletion?

### Production, Security, and Operations

25. How was p95 calculated exactly and what was the load?
26. What is the difference between `/health`, `/ready`, and task success?
27. What alert did you test and how long did it take to detect/recover?
28. What is in your traces that could be personal data?
29. How do you rotate a leaked secret and how do you know where it was used?
30. What happens if the provider returns 429 for ten minutes?
31. How do you rollback model/prompt/corpus in addition to code?
32. Which threat model attack have you not yet mitigated?
33. How do you prevent a tenant from seeing another's cache, memory, or chunks?
34. What artifacts verify that the deployed image is the reviewed one?

### Models, Cost, and Decision

35. Which exact models and snapshots did you run, and when did you verify the catalog?
36. Why does that path use Luna/Terra/Sol —or your current tiers— and not another?
37. What happens to quality, cost, and p95 if you force the smallest tier?
38. What is the p95 cost per successful task, including retries and evals?
39. At what volume does self-hosting become cost-effective and what operational cost did you include?
40. Which assumption in your 100× projection is the most fragile?
41. If your model is withdrawn tomorrow, what gate decides the replacement?
42. What would the next decision be with real production data?

## How to Respond

Use the sequence **decision → alternative → evidence → limit**:

> We chose hybrid retrieval because queries with IDs failed with semantics alone. In 50
> cases, recall@4 increased from result A to B with X ms in p95. We discarded pure semantics; the limit
> is that the lexical index adds operation and invalidation, documented in ADR-003.

Replace A/B/X with your actual results. If you did not measure something, say so and explain the experiment you
would run; inventing a number destroys credibility.

## Final code review

Have five points ready: HTTP input to response, graph router, a tool with error and
idempotency, retrieval+citations, and telemetry. The reviewer can choose any line: remove dead code,
unnecessary dependencies, and secrets before freezing the version.
