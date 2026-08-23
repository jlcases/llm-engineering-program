# 03 — Progress, concurrency, and loop evaluation

Finishing within budget does not prove a loop is good. It must advance toward the outcome, use
concurrency without breaking invariants, and degrade diagnostically when the world does not
cooperate.

## 1. Progress signals

Step count measures activity, not progress. Define markers external to model text:

- failing tests dropping from five to two;
- pending entities dropping from one hundred to twenty;
- evidence coverage increasing;
- remote state advancing from `queued` to `accepted`;
- calibrated uncertainty decreasing with new evidence.

Normalize the marker to detect equivalent states. Two differently worded plans may represent the
same dead end.

## 2. Unproductive cycles

Retain a state-and-action signature. If it reappears without new evidence, apply a policy:

1. first cycle: summarize the blockage and require an alternative;
2. second cycle: change capability, reduce scope, or request a different observation;
3. final cycle: terminate in `exhausted` or `needs_human`.

Increasing `max_steps` in response to a cycle only makes the same failure more expensive.

## 3. Structured concurrency

Parallelize independent work, not decisions that write the same state without a reducer. For every
fan-out define:

- immutable input set;
- worker and queue limit;
- budget reserved per branch;
- aggregation order or key;
- partial-failure policy;
- cancellation of branches once enough outcome exists.

The reducer must be associative and, when order is irrelevant, commutative. Otherwise serialize or
record order as part of the contract.

## 4. Backpressure

The loop must not create work faster than executors and external systems can absorb it. Control
admission through semaphores, queue size, and per-tenant quotas. Propagate 429s and load signals to
the planner as state, not text inviting it to insist.

Measure queue time separately from execution time. High latency caused by backpressure is not fixed
by choosing a faster model.

## 5. Trajectory quality

Evaluate separate dimensions:

| Dimension | Example metric |
|---|---|
| Outcome | Verified task rate |
| Progress | Useful steps / total steps |
| Efficiency | Tokens, cost, and time per success |
| Robustness | Success under injected errors |
| Safety | Violations and unapproved effects |
| Durability | Correct resumptions / crashes |
| Intervention | Correct and avoidable escalations |

Segment by task and failure type. An average can hide a loop that works for reads but duplicates
writes under timeout.

## 6. Deterministic simulation

Before spending tokens, run the loop with programmed planners and executors:

- happy sequence;
- transient error followed by success;
- permanent permission denial;
- repeated observation;
- cancellation between two actions;
- crash inside the ambiguity window;
- old checkpoint;
- two branches competing for budget.

Simulation tests control. Model evaluations test decisions inside that control. If you mix the two
layers, every failure becomes more expensive and harder to locate.

## 7. Operating the loop

Expose metrics for runs by state, age of `running`, terminal reason, steps, cost, pending receipts,
and resumptions. Alert on impossible states: runs without a next alarm, ambiguous intents that are too
old, or sequences moving backward.

The operational view must answer within minutes: what is stuck, what effect may be uncertain, and
which version produced the behavior.
