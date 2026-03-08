# OpenClaw Integration

OpenClawBrain integrates with OpenClaw through a narrow promoted-pack boundary.

## Integration contract

OpenClaw keeps the hot path: session flow, prompt assembly, response delivery, and fail-open serving.

OpenClawBrain supplies the learning side of the boundary:

- normalized event contracts
- deterministic event export and provenance
- immutable pack materialization
- activation staging and promotion
- promoted-pack compilation with learned-route diagnostics

Today that learning boundary refreshes candidate packs behind the hot path. The current code does not prove in-place mutation of the active pack during serving.

## Top invariant

The promoted pack is the only supported artifact OpenClaw should compile from.

If that pack's manifest says learned routing is required, compilation must use the pack's learned `route_fn`, expose `routerIdentity`, and report `usedLearnedRouteFn=true`.

That local promoted-pack proof is the center of the current OpenClawBrain story.
The broader route-function, traversal-learning, and `QTsim` benchmark story remains important, but it belongs to the separate Brain Ground Zero proof track rather than this repo's local implementation claims.

## Minimal package surface

Start with the narrow package set:

```bash
pnpm add @openclawbrain/contracts @openclawbrain/events @openclawbrain/event-export @openclawbrain/learner @openclawbrain/activation @openclawbrain/compiler
```

Add these when needed:

- `@openclawbrain/pack-format`
- `@openclawbrain/workspace-metadata`
- `@openclawbrain/provenance`
- `@openclawbrain/openclaw` for the typed OpenClaw bridge package itself

The supported public integration boundary is the versioned `@openclawbrain/*` package set plus versioned fixtures under `contracts/`.
For the current wave, treat the repo tip and `.release/` tarballs as the truthful distribution surface unless `pnpm release:status` shows a matching release tag on `HEAD`.

## Bring-up sequence

From the repo root:

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm check
pnpm release:status
pnpm release:pack
```

## Attach sequence

The intended attach path is:

1. Bootstrap from current workspace state and recent normalized events.
2. Materialize a fast-boot pack quickly.
3. Promote that pack so OpenClaw can compile useful context immediately.
4. Keep live event ingestion running continuously.
5. Keep passive backfill and candidate-pack refresh running behind the hot path.
6. Promote fresher candidate packs as they become activation-ready.

Do not gate first value on a full historical replay.

## Proofs available in this repo today

Use the built-in smoke lanes:

```bash
pnpm lifecycle:smoke
pnpm observability:smoke
pnpm continuous-product-loop:smoke
```

These prove:

- pack materialization from normalized inputs
- activation staging and promotion
- compilation against promoted packs
- learned `route_fn` evidence and explicit fallback notes
- seed-state bootstrap followed by later PG-promoted handoff
- operator-facing health and freshness diagnostics

They run against the public package surface in this repo and temporary activation state. The central local proof is still learned `route_fn` usage at the promoted-pack boundary.

## Failure semantics

Integration stays fail-open:

- OpenClaw continues serving if learning or artifact refresh is delayed
- compile can fall back deterministically when token selection misses
- learning, harvesting, structural graph updates, and pack refresh stay off the hot path and land through candidate-pack promotion

## Related docs

- [docs/setup-guide.md](setup-guide.md)
- [docs/operator-guide.md](operator-guide.md)
- [docs/worked-example.md](worked-example.md)
- [docs/reproduce-eval.md](reproduce-eval.md)
