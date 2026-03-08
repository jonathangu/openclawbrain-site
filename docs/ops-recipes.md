> Canonical docs live on GitHub; this page is a trimmed operator snapshot for the current public wave.

# OpenClawBrain Ops Recipes

## Recipe 1: Day-0 attach bootstrap

Goal: attach quickly and get first value without waiting for a full replay.

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm check
pnpm release:status
pnpm lifecycle:smoke
pnpm observability:smoke
```

Expected result:

- a fast-boot pack can be materialized and promoted quickly
- OpenClaw can compile useful context immediately after attach
- live events can start learning while older history backfills later

## Recipe 2: Inspect ship surface before any release claim

Goal: keep repo-tip, tagged-candidate, and published-wave language separate.

```bash
pnpm release:status
```

Check for:

- `shipSurface`
- matching tag on `HEAD`
- proof-gate status
- blocking reasons
- linked proof bundle counts

If the surface is still `repo-tip`, do not market the wave as a finished publish.

## Recipe 3: Verify learned-route authority

Goal: prove that the served compile used the promoted pack's learned router when required.

Use:

- `pnpm observability:report`
- compile diagnostics showing `usedLearnedRouteFn=true`
- compile diagnostics exposing `routerIdentity` and router checksum
- handoff notes showing whether the runtime is still on seed state or has handed off to a later PG-promoted pack

## Recipe 4: Handle stale learning safely

Goal: keep serving stable while background learning catches up.

If learning is stale or delayed:

- keep OpenClaw serving through the current promoted pack
- keep fail-open behavior explicit
- repair live-event flow before deep backlog work
- promote only activation-ready candidate packs

## Recipe 5: Rollback check

Goal: prove rollback readiness instead of assuming it.

```bash
pnpm observability:report
```

Inspect:

- `rollback.before`
- `activationSlots.rolledBack`
- `freshnessTargets.rolledBackActive`
- `freshnessTargets.rolledBackCandidate`

## Recipe 6: Keep the proof boundary honest

Use these phrases:

- promoted-pack compile proof
- PG-only learned `route_fn` evidence
- later served-turn change after promotion
- broader traversal-learning and `QTsim` story lives in Brain Ground Zero

Avoid these phrases:

- live active-pack mutation proved here
- per-query router updates on the current active pack
- finished design-partner polish or broad public launch
