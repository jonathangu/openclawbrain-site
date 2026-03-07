# OpenClaw Integration

OpenClawBrain is a learning layer that plugs into OpenClaw. OpenClaw owns the runtime (sessions, tools, prompts, answers). OpenClawBrain owns learning: it turns usage, feedback, and history into brain packs that improve what context gets served at query time.

New here? Start with the [setup guide](setup-guide.md).

Other docs:
- [Operator runbook](operator-guide.md)
- [Operational playbooks](ops-recipes.md)
- [New agent onboarding](new-agent-sop.md)

## Who owns what

### OpenClaw (runtime)

- Sessions, prompt assembly, and serving responses
- Fail-open behavior: if brain degrades, the agent keeps working
- Deployment, routing, and rollback controls

### OpenClawBrain (learning)

- Contracts and event schemas
- Event normalization and export
- Workspace metadata extraction and provenance
- Brain pack format, activation helpers, compiler, and learner

## Package surface

The integration is built from these packages:

- `@openclawbrain/contracts`
- `@openclawbrain/events`
- `@openclawbrain/event-export`
- `@openclawbrain/workspace-metadata`
- `@openclawbrain/provenance`
- `@openclawbrain/pack-format`
- `@openclawbrain/activation`
- `@openclawbrain/compiler`
- `@openclawbrain/learner`

## Build and deploy

```bash
corepack enable
pnpm install
pnpm check
pnpm release:pack
```

OpenClaw runtime then deploys the released pack set in its own environment.

## Runtime behavior

### Serving (hot path)

1. OpenClaw receives a query.
2. The learned route function (from the deployed brain pack) picks which context blocks to surface.
3. OpenClaw assembles the prompt with that context and serves the response.

### Learning (off the hot path)

These run asynchronously and never slow down responses:

- Events are normalized and harvested continuously
- Scanner processes workspace and event streams
- Human and self labels are collected by default
- Graph learning (decay, co-firing, structural updates) runs continuously

Teacher logic stays off the hot path.

## Fast boot

The runtime starts serving immediately from existing workspace files and prior exports. Background learning backfills historical data while prioritizing new events first. This keeps startup fast even with large archives.

## Fail-open behavior

The integration is designed to be fail-open:

- If learning/scanner/harvest workers are delayed, OpenClaw still serves responses normally
- If brain quality degrades, OpenClaw falls back to core runtime behavior
- Recovery happens via background loops and pack rollback

## Proof boundary

Two categories of proof, kept separate:

- **Mechanism proof** (required): contracts compile, events normalize correctly, provenance is intact, route function evaluates deterministically
- **Product proof** (separate): user-visible quality, error reduction, correction retention under live traffic

Mechanism proof is required but not sufficient for product claims.
