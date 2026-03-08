# OpenClaw Integration

OpenClawBrain integrates with OpenClaw through a narrow promoted-pack boundary.

## Integration contract

OpenClaw keeps the hot path: session flow, prompt assembly, response delivery, and fail-open serving.

OpenClawBrain supplies the learning side of the boundary:

- normalized event contracts
- deterministic event export and provenance
- immutable pack materialization
- activation staging/promotion
- promoted-pack compilation with learned-route diagnostics

Today that learning boundary refreshes candidate packs behind the hot path. The current code does not prove in-place mutation of the active pack during serving.

`describeAttachStatus()` in `@openclawbrain/openclaw` exposes this as `landingBoundaries` so the attach surface can state the real handoff instead of implying hidden runtime overlap.

## Top invariant

The promoted pack is the only supported artifact OpenClaw should compile from.

If that pack's manifest says learned routing is required, compilation must use the pack's learned `route_fn`, expose `routerIdentity`, and report `usedLearnedRouteFn=true`.

## Exact landing path

The concrete landing sequence into OpenClaw is:

1. OpenClaw calls `compileRuntimeContext()` or `runRuntimeTurn()` from `@openclawbrain/openclaw`.
2. That bridge resolves activation's `active` pointer and calls `@openclawbrain/compiler.compileRuntimeFromActivation()`.
3. Compiler serves only from the active promoted pack and emits learned-route / fallback diagnostics.
4. `runRuntimeTurn()` separately emits normalized interaction / feedback artifacts for learner handoff.
5. Learner materializes fresher candidate packs off the hot path.
6. Activation stages and promotes only activation-ready candidates.
7. Later OpenClaw compiles see the fresher pack only after promotion flips the pointers.

Boundary-by-boundary, that means:

- `compile boundary`: promoted active pack only; candidate packs are never served before promotion
- `event export boundary`: turn export is a side-channel handoff for later learning, not an in-place mutation of the active pack
- `active pack boundary`: `active` is compile-visible; `candidate` and `previous` are inspectable for promotion / rollback only
- `promotion boundary`: freshness advances by staging then promoting a newer candidate, not by mutating the currently served pack
- `fail-open semantics`: missing active packs fail open; learned-required route-artifact drift hard-fails; event-export write failures do not erase successful compile output
- `runtime ownership`: OpenClaw remains responsible for session/runtime orchestration, prompt assembly, response delivery, and the final guarded serve-path decision

## Migration from heavy raw workspace injection

If your current OpenClaw integration still pushes a large raw workspace dump into every turn, do not jump straight to full replacement.

Use this sequence instead:

1. supplement the current raw injection with promoted-pack compile
2. shadow-compare the compiled result and freshness diagnostics
3. replace one bounded memory-like slice at a time
4. end with a tiny direct kernel plus compiled brain memory

That rollout keeps the promoted-pack boundary truthful: the active pack is still the only compile-visible artifact, candidate freshness stays off the hot path until promotion, and learned-required route evidence remains explicit.

The detailed migration checklist lives in [raw-workspace-migration.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/raw-workspace-migration.md).

## Minimal package surface

For the current wave, do not assume bare registry install.
Use the repo tip plus `.release/` tarballs unless `pnpm release:status` shows a matching release tag on `HEAD` and the later publish lane has completed.

When that later lane is live, start with the narrow package set:

```bash
pnpm add @openclawbrain/contracts @openclawbrain/events @openclawbrain/event-export @openclawbrain/learner @openclawbrain/activation @openclawbrain/compiler
```

Add these when needed:

- `@openclawbrain/pack-format`
- `@openclawbrain/workspace-metadata`
- `@openclawbrain/provenance`
- `@openclawbrain/openclaw` for the typed OpenClaw bridge package itself

The supported public integration boundary is the versioned `@openclawbrain/*` package set plus versioned fixtures under `contracts/`.

## Bring-up sequence

From the repo root:

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm check
pnpm release:status
pnpm release:pack
```

## Proofs available in this repo today

Use the built-in smoke lanes:

```bash
pnpm lifecycle:smoke
pnpm observability:smoke
```

These prove:

- pack materialization from normalized inputs
- activation staging and promotion
- compilation against promoted packs
- learned `route_fn` evidence and explicit fallback notes
- operator-facing health and freshness diagnostics

They run against the public package surface in this repo and temporary activation state. The central local proof is still learned `route_fn` usage at the promoted-pack boundary.

Broader comparative benchmark families and the route-function / `QTsim` proof story live in the sibling public repo `brain-ground-zero`. See `CLAIMS.md` for the exact split.

## Failure semantics

Integration stays fail-open, but only within the actual served-boundary rules:

- OpenClaw continues serving if learning or artifact refresh is delayed
- missing active packs and non-learned-required compile misses can fall back explicitly
- learned-required route-artifact drift is a hard serve-path failure, not a silent fallback case
- event-export bundle write failures do not erase successful compile output
- learning, harvesting, structural graph updates, and pack refresh stay off the hot path and land through candidate-pack promotion

## Related docs

- [openclaw-attach-quickstart.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/openclaw-attach-quickstart.md)
- [operator-observability.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/operator-observability.md)
- [reproduce-eval.md](reproduce-eval.md)
- [learning-first-convergence.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/learning-first-convergence.md)
