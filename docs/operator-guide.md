> Canonical observability details live on GitHub; this page mirrors the operator truth for the current launch wave.

# OpenClawBrain Operator Guide

## Current operating truth

Treat the current public wave as an external technical alpha.

- the implementation reality is the current public repo tip on `openclawbrain` `origin/main`, not a private unpublished branch
- the truthful shipping surface is repo tip plus optional `.release/` tarballs
- release-proof gates are still pending until `pnpm release:status` says otherwise
- docs should not imply a finished registry wave or broad-customer polish

## What healthy operation means today

A healthy attached runtime looks like this:

- first value appears from a fast-boot promoted pack before any full replay finishes
- live events keep landing while older history backfills behind the hot path
- learned-routing proof stays explicit whenever the promoted pack requires it
- freshness, promotion, rollback lineage, and no-op reasons are inspectable
- OpenClaw stays fail-open if learning refresh is delayed

## Required commands

From the repo root, use these checks first:

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm check
pnpm release:status
pnpm observability:smoke
pnpm observability:report
```

Use these when you want attach-specific confidence:

```bash
pnpm lifecycle:smoke
pnpm continuous-product-loop:smoke
pnpm runtime-wrapper-path:smoke
```

## What to inspect

Read the proof surfaces in this order:

1. `pnpm release:status` for ship surface, tag state, proof-gate status, and blocking reasons.
2. `pnpm observability:report` for activation slots, freshness targets, rollback lineage, route artifact diffs, init handoff, and duplicate no-op reporting.
3. compile diagnostics for `usedLearnedRouteFn`, `routerIdentity`, router checksum, PG objective metadata, and explicit fallback notes.

If `handoff_state=seed_state_authoritative`, the runtime is still on the fast-boot seed-state pack.
If `handoff_state=pg_promoted_pack_authoritative`, a later PG-promoted pack has become authoritative.

## Claim boundary for operators

The public operator proof today is narrow but real:

- promoted-pack compilation is real
- learned `route_fn` evidence is real
- Eagle/Tern dogfood proves passive learning on attached installs: exports land, candidate packs promote, and later served turns reflect learned route and graph changes
- the default `bge-large` embedder path is real on attached installs
- optional local `qwen3.5:9b` teacher enablement is real on attached installs
- explicit fallback visibility is real

Do not treat these as proof of:

- per-query or same-turn learned `route_fn` mutation on the active pack
- broad operator hardening across many profiles or environments
- finished shadow or online answer-quality proof
- full local reproduction of the broader traversal-learning and `QTsim` benchmark story

That broader route-function story remains important; benchmark superiority is still claimed through Brain Ground Zero, not through this repo alone.
