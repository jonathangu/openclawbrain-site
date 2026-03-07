> Canonical docs live on GitHub; this page is a snapshot.

# OpenClawBrain Ops Recipes (TypeScript-first)

Practical operator playbooks for the package-first runtime model.

Canonical runbook: [docs/operator-guide.md](operator-guide.md)

## Recipe 1: Day-0 bootstrap from existing files

Goal: start serving quickly without waiting for full historical replay.

```bash
corepack enable
pnpm install
pnpm check
pnpm release:pack
```

Runtime profile requirements:
- `fastBootFromExistingFiles = true`
- `backgroundLearning.enabled = true`
- `backgroundLearning.prioritizeNewEvents = true`
- `labels.human = true`
- `labels.self = true`
- `scanner.enabled = true`
- `harvest.enabled = true`
- `continuousGraphLearning.enabled = true`

Expected result:
- runtime serves immediately from existing files/exports
- new events are learned first
- historical learning continues in background

## Recipe 2: Safe pack-set cutover

Goal: ship a new OpenClawBrain package set without disrupting serving.

1. Build and verify pack set:

```bash
corepack enable
pnpm install
pnpm check
pnpm release:pack
```

2. Deploy to canary runtime slice.
3. Validate:
- hot-path latency unchanged
- fail-open still works
- background loops healthy
4. Promote globally.

If canary fails, roll back to the previous pack set immediately.

## Recipe 3: Backlog catch-up without hot-path risk

Goal: reduce historical backlog while keeping serving stable.

1. Keep hot path on learned route function.
2. Keep teacher off hot path.
3. Reserve async worker budget for new events first.
4. Use remaining capacity for historical backfill, scanner, and harvest.
5. Watch backlog depth and new-event lag separately.

Do not gate serving on backlog completion.

## Recipe 4: Label pipeline hardening

Goal: keep human + self labels as default behavior and avoid silent drift.

1. Keep both human and self labels enabled.
2. Keep scanner/harvest enabled.
3. Monitor per-source label throughput:
- human labels accepted
- self labels accepted/rejected
- harvest application rate
4. Alert on prolonged zero-throughput windows.

A zero-throughput label pipeline usually means quality regresses before hot-path errors appear.

## Recipe 5: Continuous graph learning tuning

Goal: keep live graph adaptation active without overfitting.

Required defaults:
- decay enabled
- Hebbian co-firing enabled
- structural updates enabled

Tuning order:
1. Stabilize hot-path latency and fail-open behavior.
2. Stabilize new-event learning lag.
3. Tune decay/co-firing/structure rates incrementally.
4. Re-check correction retention and repeat-error trend.

## Recipe 6: Runtime rollback on quality regression

Goal: recover quickly when product quality drops after promotion.

1. Revert OpenClaw runtime to previous known-good pack set.
2. Keep serving active with fail-open.
3. Preserve event exports and provenance for analysis.
4. Compare mechanism metrics vs product outcomes:
- mechanism may remain healthy while product quality regresses
5. Roll forward only after a verified fix.

## Recipe 7: New agent bring-up

Use [docs/new-agent-sop.md](new-agent-sop.md) for full steps.

Minimum policy checklist for a new agent:
- dedicated workspace
- dedicated brain profile in OpenClaw runtime
- package set pinned
- fast boot enabled
- background learning enabled
- labels/scanner/harvest enabled
- teacher off hot path
