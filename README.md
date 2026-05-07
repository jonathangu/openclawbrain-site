# openclawbrain.ai

Source for [openclawbrain.ai](https://openclawbrain.ai).

This is the lightweight product site for OpenClawBrain. It should answer:

- What is this?
- Why should I care?
- Can I trust it?

Keep the site short and readable. GitHub is the operator/developer truth page for install, config, verification, endpoints, and debugging.

Shared spine:

> Evidence, not vibes, for agent memory.
>
> OpenClawBrain is local, accountable memory for OpenClaw agents. It remembers durable corrections, preferences, workflows, and context, then learns when that memory should affect a future turn.
>
> LLM decides semantic meaning. Code enforces trust boundaries. SQLite stores the graph and evidence.

Current public truth:

- Current release: `0.2.21`.
- Production routing path: route-policy-v3 first.
- Fallback and rollback path: route-policy-v2, then legacy heuristics.
- Learning loop: redacted route frames, SQLite evidence, shadow decisions, replay/eval cases, calibration examples, action-family stats, candidate reports, gated promotion, and rollback lineage.

Shareable summary:

> OpenClawBrain is a local-first memory system for AI agents. The core idea: an agent should not just “remember everything.” It should learn when memory actually matters. OpenClawBrain turns corrections, outcomes, misses, and handoffs into local evidence, then learns a small routing policy that decides when to bring the right memory into a future turn — or abstain when it is not confident. The LLM proposes meaning; code owns validation, storage, calibration, promotion, and rollback. SQLite keeps the graph and evidence local and inspectable.
