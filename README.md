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

- Current release: `0.2.22`.
- Public ultimate guide: `/guide/` explains the architecture history, failed iterations, core route-learning loop, and AI-building lessons.
- Public Memory Authority guide: `/memory-authority/` explains why relevant memory is not automatically authorized memory.
- Public live visual: `/live/` shows the redacted local runtime, SQLite graph shape, and a real useful memory-injected turn.
- Production routing path: route-policy-v3 first.
- Authority path: retrieved memories can be injected, weakened, verified, confirmed, suppressed, tombstoned, or withheld before they touch the prompt.
- Fallback and rollback path: route-policy-v2, then legacy heuristics.
- Learning loop: redacted route frames, SQLite evidence, shadow decisions, replay/eval cases, calibration examples, action-family stats, candidate reports, gated promotion, and rollback lineage.

Shareable summary:

> OpenClawBrain is a local-first memory system for AI agents. The core idea: an agent should not just “remember everything.” It should learn when memory actually matters, then check whether retrieved memory still has authority. OpenClawBrain turns corrections, outcomes, misses, and handoffs into local evidence, learns a small routing policy, and resolves authority before memory reaches the prompt. The LLM proposes meaning; code owns validation, storage, calibration, promotion, rollback, and forgetting. SQLite keeps the graph and evidence local and inspectable.
