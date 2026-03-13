> Canonical observability detail still lives on GitHub; this page mirrors the operator truth for the current launch wave in plain language.

# OpenClawBrain Operator Guide

Use this page when you need fast answers to the questions operators actually ask under pressure: did attach land cleanly, what is healthy right now, and where does the proof line stop?

## Current operating truth

Treat the current public wave as a technical alpha, not finished enterprise packaging.

- The implementation truth is the public `openclawbrain` repo tip on `origin/main`, not a private unpublished branch.
- The honest shipping surface is repo tip plus optional `.release/` tarballs.
- Release-proof gates are still pending until `pnpm release:status` says otherwise.
- The docs should read like field notes from a real system, not like a polished registry wave that already shipped everywhere.

## What healthy looks like today

A healthy attached runtime looks like this:

- First value shows up from a fast-boot promoted pack before any full replay finishes.
- New live events keep landing while older history backfills behind the hot path.
- Learned-routing proof stays explicit whenever the promoted pack requires it.
- Freshness, promotion history, rollback lineage, and no-op reasons are visible instead of hidden.
- OpenClaw stays fail-open if learning refresh is delayed.

## First commands to run

If you are triaging from the source repo, start here:

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm check
pnpm release:status
pnpm observability:smoke
pnpm observability:report
```

When you want attach-specific confidence, run these next:

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

Those are the check-in surfaces. Keep install, load, export, and later served learning separate instead of flattening them into one green check.

If `handoff_state=seed_state_authoritative`, the runtime is still serving from the fast-boot seed-state pack. If `handoff_state=pg_promoted_pack_authoritative`, a later PG-promoted pack has taken over.

## How to read the current proof line

The public operator proof today is narrow, but it is real:

- promoted-pack compilation is real
- learned `route_fn` evidence is real
- Eagle/Tern dogfood proves passive learning on attached installs: exports land, candidate packs promote, and later served turns reflect learned route and graph changes
- the default `bge-large` embedder path is real on attached installs
- optional local `qwen3.5:9b` teacher enablement is real on attached installs
- attach plus EXTERNAL RESTART is real on live profiles
- explicit fallback visibility is real

Do not stretch that into claims we have not earned yet:

- per-query or same-turn learned `route_fn` mutation on the active pack
- full live active-pack plasticity while traffic is flowing
- broad operator hardening across many profiles or environments, including shared-root concurrency safety
- finished shadow or online answer-quality proof
- full local reproduction of the broader traversal-learning and `QTsim` benchmark story

That broader route-function story still matters. It is simply claimed through Brain Ground Zero, not through this repo alone.

## Rollback mindset

If something smells wrong, treat rollback, disable, or uninstall as normal operator tools, not an admission of failure. The system is designed so you can inspect the active state, preview the pointer move, and back out cleanly without taking OpenClaw down with it.
