# OpenClaw Integration

OpenClawBrain is the TypeScript-first package surface behind the OpenClaw-owned runtime boundary. The promoted pack is the only supported learning and serve boundary in this repo.

> **Current truth**: the learner builds candidate packs off the hot path; activation stages and promotes them; compiler serves only from the active promoted pack; route updates are PG-only from explicit labels.
> **Target end shape**: continuous live graph update (decay, co-firing, pruning, reorganizing) on the active pack during serving; scanner/labels/harvest on by default after attach; hard API enforcement of the OpenClaw/OpenClawBrain split.

New here? Start with the [setup guide](setup-guide.md).

Other docs:
- [Operator runbook](operator-guide.md)
- [Operational playbooks](ops-recipes.md)
- [New agent onboarding](new-agent-sop.md)

## Who owns what

### OpenClaw (runtime)

- Sessions, prompt assembly, and serving responses
- Fail-open behavior: if brain degrades, the agent keeps working
- Deployment, routing, and rollback controls

### OpenClawBrain (learning)

- Contracts and event schemas
- Event normalization and export
- Workspace metadata extraction and provenance
- Pack format, activation helpers, compiler, and learner
- `@openclawbrain/openclaw` — typed OpenClaw bridge: compile diagnostics, learned-route hard-fail enforcement, and normalized event export handoff

The `active` promoted pack is the only serve-visible slot. `candidate` and `previous` stay inspectable for promotion and rollback. Missing active packs fail open, but learned-required route-artifact drift returns `hardRequirementViolated=true` and disables static fallback.

## Packages

The integration is split into focused npm packages, each handling one piece of the learning pipeline:

- `@openclawbrain/contracts`
- `@openclawbrain/events`
- `@openclawbrain/event-export`
- `@openclawbrain/workspace-metadata`
- `@openclawbrain/provenance`
- `@openclawbrain/pack-format`
- `@openclawbrain/activation`
- `@openclawbrain/compiler`
- `@openclawbrain/learner`
- `@openclawbrain/openclaw`

## Build and deploy

```bash
corepack enable
pnpm install
pnpm check
pnpm release:pack
```

OpenClaw runtime then deploys the released pack set in its own environment.

## Runtime behavior

### Serving (hot path)

1. OpenClaw receives a query.
2. The learned `route_fn` (from the deployed brain pack) walks the knowledge graph and picks which context blocks to surface. It blends the graph's structural knowledge (`graph_prior`) with per-query relevance (`QTsim`), using a confidence gate to shift weight between them.
3. OpenClaw assembles the prompt with that bounded context and serves the response.

### Learning (off the hot path)

These run asynchronously and never add latency to responses:

- Events (corrections, feedback, usage signals) are collected and normalized
- Scanner watches for new workspace files and event streams
- Human, self, scanner, and teacher labels are collected inputs to PG-only route training
- The learner materializes fresher candidate packs off the hot path; `activation` stages and promotes them; the compiler then serves from the newly promoted pack
- Teacher logic stays off the hot path

**Graph-dynamics today**: decay settings, Hebbian co-firing settings, and split/merge/prune/connect counts are recorded inside the immutable pack artifact as **build-time metadata**. This is not the same as live runtime mutation of the active pack during serving.

**Graph-dynamics target**: continuous live update (decay, Hebbian co-firing, pruning, reorganizing) on the active pack during serving. This is the target end shape; it is not proved in this repo today. See [CLAIMS.md](https://github.com/jonathangu/openclawbrain/blob/main/CLAIMS.md) for the authoritative boundary.

## Fast boot

The runtime starts serving immediately from existing workspace files. Bootstrap attach self-boots truthfully even from zero live events; the zero-event seed state is operator-visible rather than failing at init. Background learning exports new events first, then backfills historical data.

Use `pnpm operator:status`, `pnpm operator:doctor`, and `pnpm operator:rollback -- --dry-run` for day-0 triage once you have a real activation root.

## Fail-open behavior

The integration is designed to be fail-open:

- If learning/scanner/harvest workers are delayed, OpenClaw still serves responses normally
- If the brain becomes unavailable or quality degrades, OpenClaw falls back to core runtime behavior
- Recovery happens via background loops and pack rollback

## Proof boundary

Three levels, kept separate:

- **Repo-local smoke-lane proof** (this repo): contracts compile, events normalize, pack lifecycle works, PG-only `route_fn` evidence verified, operator observability passes. Run `pnpm lifecycle:smoke`, `pnpm observability:smoke`, `pnpm continuous-product-loop:smoke`, `pnpm fresh-env:smoke`.
- **Comparative benchmark proof** (Brain Ground Zero): recorded-session H2H (0.975 vs 0.896, +7.9 pp) and sparse-feedback 10-seed (91.96% vs 67.05%, +24.91 pp) are published in the separate [brain-ground-zero](https://github.com/jonathangu/brain-ground-zero) repo. These are frozen-workload benchmark claims, not live production claims.
- **Live product proof** (not yet): shadow-mode and narrow online rollout artifacts will be published here when those tests are complete.

See [CLAIMS.md](https://github.com/jonathangu/openclawbrain/blob/main/CLAIMS.md) for the authoritative boundary between what OpenClawBrain proves, what Brain Ground Zero proves, and what is not yet claimed.

## What to avoid

- Treating `continuousGraphLearning` config flags as proof of live runtime graph plasticity. Today, graph-dynamics fields are pack artifact metadata, not live serving-path operations.
- Claiming the `@openclawbrain/*` packages are npm-published. The current wave ships from local `.release/*.tgz` tarballs. Use `pnpm release:status` to check the honest distribution lane.
- Assuming a heuristic learned-label fallback exists in the serve path. Route updates are PG-only; there is no heuristic overlay.
