> Canonical docs live on GitHub; this page mirrors the current public setup truth.

# OpenClawBrain Setup Guide

For the current public OpenClawBrain surface, start here:

1. [docs/openclaw-integration.md](openclaw-integration.md)
2. [docs/operator-guide.md](operator-guide.md)
3. [docs/worked-example.md](worked-example.md)
4. [docs/reproduce-eval.md](reproduce-eval.md)

## Launch truth for this wave

Today the truthful launch tier is:

- technical alpha usable: yes
- design-partner ready: close, but still gated
- broad public developer launch: not claimed

The current shipping surface is the public repo tip plus locally packed tarballs from `.release/`.
Do not describe the current `0.1.1` line as a completed npm release unless `pnpm release:status` shows a matching tag on `HEAD` and the release-proof gates are closed.

## Minimal bootstrap

Run from the OpenClawBrain repo root:

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm check
pnpm release:status
pnpm release:pack
```

Interpret that output in this order:

- `shipSurface: "repo-tip"` means the truthful install lane is repo checkout plus optional local tarballs
- pending proof gates mean the package wave is still proving release readiness, not claiming a finished publish
- local tarballs are for external technical-alpha installs when you want the current package split without overclaiming registry availability

## Default install lane

For the narrow attach lane, start with:

```bash
pnpm add @openclawbrain/contracts @openclawbrain/events @openclawbrain/event-export @openclawbrain/learner @openclawbrain/activation @openclawbrain/compiler
```

Add these only when needed:

- `@openclawbrain/pack-format`
- `@openclawbrain/workspace-metadata`
- `@openclawbrain/provenance`
- `@openclawbrain/openclaw` for the typed OpenClaw bridge package

## First operator checks

After install, prove the package boundary before broader rollout language:

```bash
pnpm lifecycle:smoke
pnpm observability:smoke
```

Those lanes prove the promoted-pack lifecycle, learned `route_fn` evidence at compile time, and operator-visible health/freshness signals.
They do not prove full live active-pack mutation, per-query `route_fn` updates on the current active pack, or finished shadow/online product proof.

## Central claim boundary

Keep these statements separate:

- OpenClawBrain proves the promoted-pack runtime boundary, package surface, and PG-only learned `route_fn` evidence implemented in this repo today
- the broader route-function, traversal-learning, and `QTsim` comparative proof story remains important, but it lives in the separate Brain Ground Zero proof track
- benchmark, shadow, and online claims should not be collapsed into one sentence
