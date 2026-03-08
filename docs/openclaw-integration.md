# OpenClaw Integration

OpenClawBrain is the learning layer that plugs into OpenClaw. OpenClaw owns the runtime &mdash; sessions, tools, prompts, answers. OpenClawBrain owns learning: it watches real conversations, trains a routing function (`route_fn`) over a knowledge graph, and packages the result into versioned brain packs that improve what context gets served at query time. The router learns from corrections, outcomes, and automated signals, and improves continuously without manual tuning.

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
- Brain pack format, activation helpers, compiler, and learner

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

These run asynchronously and never slow down responses:

- Events (corrections, feedback, usage signals) are collected and cleaned up continuously
- Scanner watches for new workspace files and event streams
- Human and automated feedback labels are collected by default
- The knowledge graph updates continuously: unused edges fade (decay), edges that fire together strengthen (co-firing), and the graph structure is pruned and reorganized as needed

Teacher logic stays off the hot path.

## Fast boot

The runtime starts serving immediately from existing workspace files and prior exports. Background learning backfills historical data while prioritizing new events first. This keeps startup fast even with large archives.

## Fail-open behavior

The integration is designed to be fail-open:

- If learning/scanner/harvest workers are delayed, OpenClaw still serves responses normally
- If the brain becomes unavailable or quality degrades, OpenClaw falls back to core runtime behavior
- Recovery happens via background loops and pack rollback

## Proof boundary

Two categories of proof, kept separate:

- **Mechanism proof** (required): evidence that the internals work correctly. Contracts compile, events normalize as expected, provenance is intact, and the route function produces the same output given the same input. A prerequisite for any claim.
- **Product proof** (separate): evidence that real users see better results. Does answer quality improve? Do errors go down? Are corrections retained under live traffic? This requires live or recorded-session evaluation beyond mechanism checks.

Mechanism proof is necessary but not sufficient for product claims. The system working correctly does not by itself prove it works *well* for users.
