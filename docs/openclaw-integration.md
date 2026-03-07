# OpenClaw Integration (TypeScript replacement)

OpenClawBrain is integrated as a TypeScript package set behind an OpenClaw-owned runtime boundary.

Primary docs:
- setup path: [docs/setup-guide.md](setup-guide.md)
- operator runbook: [docs/operator-guide.md](operator-guide.md)
- operational playbooks: [docs/ops-recipes.md](ops-recipes.md)
- new agent onboarding SOP: [docs/new-agent-sop.md](new-agent-sop.md)

## Integration contract

OpenClaw and OpenClawBrain have separate responsibilities.

### OpenClaw owns

- runtime orchestration and lifecycle
- fail-open behavior on brain degradation
- request/response hot path and prompt assembly
- deployment, routing, and rollback controls

### OpenClawBrain owns

- contracts and event schemas
- event normalization/export boundaries
- workspace metadata extraction
- provenance capture
- pack format + activation helpers
- compiler and learner behavior

This split is intentional: OpenClaw remains the serving runtime; OpenClawBrain provides the memory/learning substrate.

## Public package surface

Runtime integrations should be built from this package set:

- `@openclawbrain/contracts`
- `@openclawbrain/events`
- `@openclawbrain/event-export`
- `@openclawbrain/workspace-metadata`
- `@openclawbrain/provenance`
- `@openclawbrain/pack-format`
- `@openclawbrain/activation`
- `@openclawbrain/compiler`
- `@openclawbrain/learner`

## Bring-up sequence

From the TypeScript workspace root:

```bash
corepack enable
pnpm install
pnpm check
pnpm release:pack
```

OpenClaw runtime then deploys the released pack set in its own environment.

## Runtime behavior (default)

### Hot path (serving)

1. OpenClaw receives a user turn.
2. OpenClaw calls the learned route function from the deployed pack set.
3. OpenClaw assembles prompt context from selected activations.
4. OpenClaw serves response.

### Off path (asynchronous)

- new events are normalized and harvested continuously
- scanner flow runs continuously against workspace/event streams
- human and self labels are harvested by default
- continuous graph learning runs by default:
  - decay
  - Hebbian co-firing
  - structural graph updates

Teacher logic remains off the hot path and updates behavior asynchronously.

## Fast boot model

Fast boot from existing files is the default operating mode:

- no full fresh-state scan gate before serving
- runtime can start from available workspace files and prior exports
- background learning backfills historical data while new data is prioritized first

This keeps startup practical even with large historical archives.

## Failure semantics

Integration must remain fail-open:

- if a learning/scanner/harvest worker is delayed, OpenClaw still serves
- if brain quality degrades, OpenClaw falls back to core runtime behavior
- recovery happens via background loops and pack roll-forward/rollback

## Proof boundary (required)

Keep proofs honest:

- mechanism proof: contracts compile, events normalize correctly, provenance is intact, route function evaluates deterministically
- product proof: user-visible quality, error reduction, correction retention, and reliability under live traffic

Mechanism proof is required but not sufficient for product claims.

## What to avoid

- Python daemon/socket lifecycle as integration shape
- adapter-CLI-on-hot-path architecture as default model
- migration framing that treats the TypeScript package model as temporary
- full-history replay gating before first useful response
