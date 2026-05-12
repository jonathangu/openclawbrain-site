# openclawbrain.ai

Source for [openclawbrain.ai](https://openclawbrain.ai).

This is the lightweight product site for OpenClawBrain. It should answer:

- What is this?
- Why should I care?
- Can I trust it?

Keep the site short and readable. GitHub is the operator/developer truth page for install, config, verification, endpoints, and debugging.

Shared spine:

> Memory authority for local AI agents.
>
> OpenClawBrain gives local agents continuity across projects, tools, and days. It remembers corrections, preferences, workflows, and handoffs, then checks whether each memory still deserves authority before it shapes the next turn.
>
> Remember what matters. Trust the current instruction. Leave proof for every important memory decision.

Current public truth:

- Current release: `0.2.31`.
- Public ultimate guide: `/guide/` explains the architecture history, failed iterations, core route-learning loop, and AI-building lessons.
- Public Memory Authority guide: `/memory-authority/` explains why relevant memory is not automatically authorized memory.
- Public Codex continuity tutorial: `/codex-continuity/` explains how Codex UI stays the workbench while OpenClaw/Telegram becomes the mobile operator surface.
- Telegram command spine: `/brain codex status`, `/brain codex threads [filter]`, `/brain codex last`, `/brain codex messages`, `/brain codex bind`, `/brain codex tail`, `/brain codex reply`, `/brain codex send`, `/brain codex steer`, `/brain codex watches`, `/brain codex unwatch`, and `/brain codex handoff`.
- Public live visual: `/live/` shows the redacted local runtime, SQLite graph shape, and a real useful memory-injected turn.
- Production routing path: route-policy-v3 first.
- Authority path: retrieved memories can be injected, weakened, verified, confirmed, suppressed, tombstoned, or withheld before they touch the prompt.
- Fallback and rollback path: route-policy-v2, then legacy heuristics.
- Learning loop: redacted route frames, SQLite evidence, shadow decisions, replay/eval cases, calibration examples, action-family stats, candidate reports, gated promotion, and rollback lineage.

Shareable summary:

> OpenClawBrain is a local-first memory system for AI agents. The core idea: an agent should not just remember more. It should know when the past is still allowed to guide the present. OpenClawBrain remembers useful corrections, preferences, workflows, and handoffs, then resolves authority before memory reaches the prompt. That makes it different from generic memory, vector notes, or transcript recall: relevance is not authority.
