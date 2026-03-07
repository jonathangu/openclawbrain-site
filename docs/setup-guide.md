> Canonical docs live on GitHub; this page mirrors the shipped setup path.

# OpenClawBrain Setup Guide (TypeScript-first)

OpenClawBrain is the shipped TypeScript-first, package-first workspace behind an OpenClaw-owned runtime boundary.

This guide is the day-0 setup path for operators who want:
- fast boot from existing files
- always-on background learning by default
- default-on labels, scanner, and harvest flow
- deterministic compile from active packs
- activation, promotion, and rollback discipline for pack sets

## Prerequisites

- Node.js 20+ and `corepack`
- `pnpm` enabled via `corepack`
- OpenClaw runtime checkout and deployment access
- existing agent workspace files (markdown/docs/memory) ready to ingest
- provider credentials configured in OpenClaw runtime secrets, not in workspace docs

## Step 1: Install and verify the workspace

Run from the OpenClawBrain TypeScript workspace root:

```bash
corepack enable
pnpm install
pnpm check
pnpm release:pack
```

`pnpm check` is the release quality gate for type/lint/test/package integrity. `pnpm release:pack` produces the versioned package/pack set consumed by OpenClaw runtime.

## Step 2: Pin the canonical package surface

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

Promote package sets as a unit. Do not mix ad-hoc local package revisions in production.

## Step 3: Wire OpenClaw runtime to the package set

OpenClaw owns runtime orchestration and fail-open behavior. OpenClawBrain packages provide memory, normalization, provenance, pack lifecycle, and compile/learning components.

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

## Step 4: Activate, promote, and rollback packs

1. Activate candidate pack set in canary runtime scope.
2. Validate latency, fail-open behavior, and loop health.
3. Promote candidate globally when canary passes.
4. Roll back to previous active pack set if health regresses.

Compilation from the active pack remains deterministic for a fixed state.

## Step 5: Validate first boot behavior

Expected first-boot behavior:

1. OpenClaw starts serving immediately from existing files and metadata.
2. Serving starts immediately from existing files and metadata.
3. New events are learned first; historical backfill continues in background.
4. Labels/scanner/harvest loops are active by default.
5. Compiled context size is chosen for task effectiveness, including larger context when it avoids extra model/tool round-trips.

## Step 6: Validate runtime boundaries

Operator checks:

- OpenClaw hot path remains available when learner/scanner work is delayed.
- Runtime fail-open behavior is verified (brain degradation does not block replies).
- Provenance is preserved for normalized events and generated activations.
- Teacher logic executes asynchronously and never gates turn latency.

## Step 7: Day-2 operating model

Default model:

- keep runtime up continuously
- keep background learning enabled continuously
- promote package sets intentionally (canary, then broad rollout)
- measure mechanism/workflow and live product outcomes separately

Mechanism/workflow proof examples:
- contract integrity
- normalization/provenance correctness
- deterministic pack/compiler behavior

Live product proof examples:
- response quality uplift
- correction durability
- retrieval precision/recall at user-visible level

Mechanism/workflow checks are required release evidence, not a substitute for live answer-quality evidence.
