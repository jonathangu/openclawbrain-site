# Getting Started with OpenClawBrain

OpenClawBrain is a second brain for your OpenClaw agent — a guide that learns which knowledge matters for each question, instead of keyword-searching every document. Think of it as hiring a librarian who gets smarter every day.

This guide is the day-0 setup path. It covers what the repo delivers today and what's coming next — clearly separated. OpenClaw owns the live runtime (front of house); OpenClawBrain owns the knowledge, learning, and context compilation (the kitchen).

> **Current truth**: promoted-pack lifecycle, learned `route_fn` evidence, operator observability, local tarball distribution, and Eagle/Tern dogfood proof for passive learning through promoted packs on attached installs.
> **Target end shape**: npm-published API, scanner/labels/harvest on by default after attach, broader operator hardening, and harder API enforcement of the OpenClaw/OpenClawBrain split.

## Operator model

The day-0 operator story is not "one brain per profile or bust." A single shared brain per machine is an acceptable default: attach each OpenClaw profile to the same activation root unless you have a reason to isolate one.

Shared brain does not mean identical context on every request. OpenClawBrain still compiles context per ask, so different prompts and profiles can retrieve different slices from the same machine-level brain.

Use a dedicated activation root when you want rollback, disable, cleanup, or blame scoped to one profile instead of the whole machine.

## What you need

- Node.js 20+ with `corepack` and `pnpm` 10+
- An OpenClaw runtime deployment (OpenClawBrain is a learning layer, not a standalone runtime)
- Workspace files (markdown, docs, memory files) for your agent to learn from
- **No provider API keys required for OpenClawBrain itself.** The default stack uses local BGE-large embeddings and an optional local Ollama teacher. The broader OpenClaw runtime may still need provider keys for its own agent and tool calls — see [Secrets and Capabilities](secrets-and-capabilities.md).
- **Distribution**: the public install surface is `npm install -g @openclawbrain/openclaw@0.3.0`. Maintainers still use `pnpm release:check` to verify the proof lane and rebuild release artifacts.

## 1. Build the workspace

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm check                  # type-check, lint, test, and verify package integrity
pnpm release:check          # full proof lane + release artifacts
pnpm fresh-env:smoke        # clean-room outside-consumer install proof
```

A **brain pack** is an immutable versioned artifact containing graph nodes, vector entries, provenance, and an optional learned `route_fn`. It is materialized off the hot path by the learner and made compile-visible only after promotion by `activation`. The compiler always serves from the currently active promoted pack.

`pnpm check` runs type-check, lint, test, lifecycle smoke, and observability smoke.
`pnpm release:check` runs the full proof lane, rebuilds release artifacts, and writes `.release/release-proof-manifest.json`.
`pnpm fresh-env:smoke` is the clean-room outside-consumer lane: installs tarballs into an isolated plain-`npm` directory and proves the attach/promotion/rollback flow.

## 2. Connect to OpenClaw

OpenClaw owns runtime orchestration. You tell it where to find the brain pack by setting a runtime profile:

```json
{
  "brain": {
    "enabled": true,
    "packSet": "<versioned-pack-set>",       // which brain pack version to load
    "fastBootFromExistingFiles": true,        // start serving immediately from existing files
    "backgroundLearning": {
      "enabled": true,
      "prioritizeNewEvents": true             // learn from new usage before backfilling history
    },
    "labels": { "human": true, "self": true },// collect human and automated feedback signals
    "scanner": { "enabled": true },           // watch for new workspace and event data
    "harvest": { "enabled": true },           // extract learning signals from events
    "teacher": { "onHotPath": false }         // keep learning off the response path
  }
}
```

Key points — **current truth**:
- `fastBootFromExistingFiles` means OpenClaw starts serving immediately. Bootstrap attach self-boots even from zero live events; the zero-event seed state is operator-visible rather than failing at init.
- `teacher.onHotPath: false` keeps learning off the hot path. Learning never adds latency to responses.
- Labels, scanner, and harvest are collected inputs to route training. They run on the learning side, not in the hot-path serve loop.
- `backgroundLearning` today means: export turns → build/refresh a candidate pack off the hot path → stage and promote → compiler serves from the newly promoted pack. Eagle and Tern now prove that passive-learning loop on attached installs. It is **not** same-turn mutation of the currently active pack during serving.
- Graph evolution is now visible on attached installs through promoted-pack changes after export and learning. That is real live operator proof, but it is still different from per-query in-place mutation of the active pack during serving.

**Target end shape** (not yet): scanner/labels/harvest on by default after attach without any config; broader operator hardening; wider rollout proof.

## 2b. Public package surface

The supported packages behind the published install surface:

- `@openclawbrain/contracts`
- `@openclawbrain/events`
- `@openclawbrain/event-export`
- `@openclawbrain/workspace-metadata`
- `@openclawbrain/provenance`
- `@openclawbrain/pack-format`
- `@openclawbrain/activation`
- `@openclawbrain/compiler`
- `@openclawbrain/learner`
- `@openclawbrain/openclaw` — typed OpenClaw bridge: compile diagnostics, learned-route hard-fail enforcement, normalized event export handoff

Use `pnpm operator:status`, `pnpm operator:doctor`, and `pnpm operator:rollback -- --dry-run` for day-0 triage once you have a real activation root.
Those commands operate on the activation root you chose: machine-wide if profiles share a root, profile-scoped if you gave one profile its own root.

## 3. Confirm it is working

After connecting, verify these behaviors:

1. **Agent responds immediately.** OpenClaw boots from the seed pack without waiting for background learning. Zero-event bootstraps stay in seed-state only until the first exported turn arrives.
2. **Background learning is running.** New events are exported first; historical backfill continues. The learner materializes candidate packs off the hot path; `activation` promotes them.
3. **Fail-open works.** If brain workers are delayed, OpenClaw still serves from the active pack. Missing active packs fail open, but learned-required route-artifact drift hard-fails instead of silently bypassing the learned path.
4. **Observability.** Run `pnpm operator:status` for a one-screen answer to: did attach land first value, what is active now, and is rollback ready? Run `pnpm operator:doctor` for explicit PASS/WARN/FAIL follow-up when `status` shows drift.

## 4. Rollback and fail-open

OpenClaw owns fail-open behavior. If something goes wrong:

- **Brain becomes unavailable:** OpenClaw automatically falls back to core runtime behavior. Responses continue without brain-enhanced context.
- **Bad brain pack:** Roll back to the previous active pack set using `pnpm operator:rollback -- --activation-root <path> --dry-run` first to preview the exact pointer move, then apply. If profiles share that activation root, the rollback applies to the shared machine brain; if the root is dedicated, the rollback stays with that profile. Compilation from a given pack is deterministic, so rollback is safe and repeatable.
- **Learning delays:** Scanner, harvest, and learner workers run asynchronously. Delays do not affect the hot path.

Recovery happens through background loops and pack rollback &mdash; no manual intervention needed.

## Next steps

- [Integration docs](openclaw-integration.md) — detailed runtime wiring, PG-only route constraint, and failure semantics
- [Reproduce benchmarks](reproduce-eval.md) — run the evaluation harness yourself
- [Proof package](/proof/) — repo-local smoke-lane proof, worked examples, and benchmark evidence (BGZ)
- [CLAIMS.md](https://github.com/jonathangu/openclawbrain/blob/main/CLAIMS.md) — authoritative repo-local boundary between what OpenClawBrain proves today and what Brain Ground Zero proves separately

## Proof lanes

Run these to verify the full promoted-pack lifecycle locally:

```bash
pnpm lifecycle:smoke            # normalized events → promoted-pack compilation
pnpm observability:smoke        # activation health, PG metadata, route artifact diffs
pnpm continuous-product-loop:smoke  # live-style export → PG-only candidate refresh → promotion
pnpm runtime-wrapper-path:smoke # OpenClaw wrapper path: compile → export → async learning → promotion
pnpm customer-value-proof:smoke # recorded-session replay showing learning changes later served turns
```
