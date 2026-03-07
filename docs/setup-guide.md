> Canonical docs live on GitHub; this page is a snapshot.

# OpenClawBrain Setup Guide (TypeScript-first)

OpenClawBrain is now a TypeScript-first, package-first workspace that runs behind an OpenClaw-owned runtime boundary.

This guide is the day-0 setup path for operators who want:
- fast boot from existing files
- always-on background learning by default
- default-on labels, scanner, and harvest flow
- continuous graph learning with teacher off the hot path

## Prerequisites

- Node.js 20+ and `corepack`
- `pnpm` enabled via `corepack`
- OpenClaw runtime checkout and deployment access
- Existing agent workspace files (markdown/docs/memory) ready to ingest
- Provider credentials configured in OpenClaw runtime secrets, not in workspace docs

## Step 1: Install and verify the workspace

Run from the OpenClawBrain TypeScript workspace root:

```bash
corepack enable
pnpm install
pnpm check
pnpm release:pack
```

`pnpm check` is the quality gate for type/lint/test/package integrity. `pnpm release:pack` produces the package set consumed by OpenClaw runtime.

## Step 2: Pin the public package surface

Use a pinned, versioned package set for runtime wiring:

- `@openclawbrain/contracts`
- `@openclawbrain/events`
- `@openclawbrain/event-export`
- `@openclawbrain/workspace-metadata`
- `@openclawbrain/provenance`
- `@openclawbrain/pack-format`
- `@openclawbrain/activation`
- `@openclawbrain/compiler`
- `@openclawbrain/learner`

Avoid mixing ad-hoc local package revisions in production. Promote package sets as a unit.

## Step 3: Wire OpenClaw runtime to the package set

OpenClaw owns runtime orchestration and fail-open behavior. OpenClawBrain packages provide the contracts, normalization, and learning components.

Use a runtime profile equivalent to:

```json
{
  "brain": {
    "enabled": true,
    "packSet": "<versioned-pack-set>",
    "fastBootFromExistingFiles": true,
    "backgroundLearning": {
      "enabled": true,
      "prioritizeNewEvents": true
    },
    "labels": {
      "human": true,
      "self": true
    },
    "scanner": {
      "enabled": true
    },
    "harvest": {
      "enabled": true
    },
    "continuousGraphLearning": {
      "enabled": true,
      "decay": true,
      "hebbianCofiring": true,
      "structuralUpdates": true
    },
    "teacher": {
      "onHotPath": false
    }
  }
}
```

## Step 4: Validate first boot behavior

Expected first-boot behavior:

1. OpenClaw starts serving immediately from existing files and metadata.
2. There is no full-history scan gate before first responses.
3. New events are learned first; historical backfill continues in background.
4. Labels/scanner/harvest loops are active by default.

## Step 5: Validate runtime boundaries

Operator checks:

- OpenClaw hot path remains available when learner/scanner work is delayed.
- Runtime fail-open behavior is verified (brain degradation does not block replies).
- Provenance is preserved for normalized events and generated activations.
- Teacher logic executes asynchronously and never gates turn latency.

## Step 6: Day-2 operating model

Default model:

- Keep runtime up continuously.
- Keep background learning enabled continuously.
- Promote package sets intentionally (canary, then broad rollout).
- Measure mechanism and product outcomes separately.

Mechanism proof examples:
- contract integrity
- normalization/provenance correctness
- deterministic pack/compiler behavior

Product proof examples:
- response quality uplift
- correction durability
- retrieval precision/recall at user-visible level

Do not claim product proof from mechanism checks alone.
