# Reproduce Evaluation + Proofs

Don't trust our numbers — run them yourself. This page walks you through regenerating every benchmark, figure, and proof artifact from scratch.

Read `CLAIMS.md` alongside this page for exact boundaries on what each test proves.

## 1) Bootstrap the workspace

```bash
cd /path/to/openclawbrain
corepack enable
pnpm install --frozen-lockfile
pnpm check
pnpm release:status
pnpm release:pack
pnpm release:proofs:status
```

## 2) Reproduce the mechanism proofs in this repo

These are the proofs implemented directly in the public package workspace today.

### Lifecycle proof

```bash
pnpm lifecycle:smoke
```

This proves the learning lifecycle across:

- normalized events
- event export
- learner pack materialization
- activation staging and promotion
- promoted-pack compilation

### Observability proof

```bash
pnpm observability:smoke
pnpm observability:report
```

This proves the operator-facing diagnostics surface for:

- activation health
- promotion freshness
- rollback readiness and rollback lineage
- supervision freshness by source
- teacher freshness
- async teacher-loop no-op detection
- learned `route_fn` freshness/version
- graph-dynamics artifact freshness
- learned `route_fn` evidence
- explicit fallback usage

`pnpm observability:report` prints the local JSON report for those proofs. It only claims what is materialized inside the repo fixture lane; it does not claim live production telemetry coverage.

Those repo-local proofs keep learned `route_fn` evidence central, but by themselves they stop at promoted-artifact freshness and later served-turn verification inside the fixture lane. The separate Eagle/Tern dogfood proof is what extends the public story to passive learning on attached installs. Neither proves same-turn in-place mutation of the active pack or live production telemetry coverage.

### Recorded-session replay proof

```bash
pnpm recorded-session-replay:smoke
pnpm recorded-session-replay:report
```

This proves the recorded-session closure lane for the checked-in sanitized replay fixture and scored bundle:

- sanitized trace → deterministic fixture conversion
- deterministic replay across `no_brain`, `seed_pack`, and `learned_replay`
- checked-in `traceHash`, `fixtureHash`, `scoreHash`, and `bundleHash` stability
- rescore verification over the checked-in bundle

See [recorded-session-replay.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/recorded-session-replay.md) for the fixture, bundle, and refresh workflow.

### OCB-native comparative eval proof

```bash
pnpm eval:ocb-native
pnpm eval:ocb-native:smoke
```

This proof lane runs the required comparative modes directly through the public OpenClaw activation + promoted-pack compile path:

- `no_brain`
- `vector_only`
- `graph_prior_only`
- `learned_route`

It emits deterministic proof artifacts under `.artifacts/ocb-native-comparative-eval/`:

- `summary_table.{md,csv,json}`
- `pairwise_delta.{md,csv,json}`
- `win_rate_matrix.{md,csv,json}`
- `per_seed_breakdowns.{md,csv,json}`
- `worked_traces.{md,json}`

The quality/context/correction numbers are explicit compile-path proxies over gold context coverage. The latency and cost columns are deterministic proxy units derived from the compile surface itself, not hand-waved prose claims and not noisy wall-clock timing.

## 3) Reproduce outside-consumer proof from local release tarballs

Use the checked-in outside-consumer smoke after `pnpm release:pack` creates `.release/` tarballs. The shortest lane is:

```bash
pnpm fresh-env:smoke
```

If you want the underlying manual outside-consumer commands instead, use:

```bash
repo_root="$(pwd)"
tmpdir="$(mktemp -d)"
cp examples/npm-consumer/package.json "$tmpdir/package.json"
cp examples/npm-consumer/smoke.mjs "$tmpdir/smoke.mjs"
cp examples/npm-consumer/attach-smoke.mjs "$tmpdir/attach-smoke.mjs"
cd "$tmpdir"
npm install "$repo_root"/.release/*.tgz
npm run smoke
npm run attach-smoke
```

This is the truthful outside-consumer proof for the current repo-only wave. It proves the current tarballs install cleanly with plain `npm`, the attach lane promotes a fresher learned pack from live-style supervision, and rollback can restore the prior active pack without claiming that the registry has already been updated.

## 4) Optional post-publish registry proof

After a matching `v0.1.2` tag has shipped and post-publish checks succeed, you can rerun the same smoke using registry versions instead of local tarball paths.

## Claim boundary

### Proven directly in this repo today

- package build and typecheck
- promoted-pack mechanism proof via lifecycle smoke
- operator observability proof via observability smoke/report
- OCB-native comparative eval + proof artifact generation over the public runtime/compile path
- versioned package surface and local tarball install path

### Maintained separately

Broader comparative benchmark families and the route-function / `QTsim` proof story that go beyond this repo's OCB-native compile/runtime proof surface still live in the separate public proof repo `brain-ground-zero`.

Use that repo's own instructions for benchmark reproduction.

When real BGZ proof bundle ids and digests are available, link them into `proofs/release-proof-input.json` and regenerate `.release/release-proof-manifest.json` with `pnpm release:proofs:manifest`.

### Not claimed here

- full comparative benchmark coverage inside this repo
- same-turn in-place graph mutation on the live active pack
- per-query learned `route_fn` updates on the active pack
- live production answer-quality proof on served OpenClaw traffic
- shadow-mode or online rollout proof
- npm publication for the current wave unless post-publish verification has been completed

## Related docs

- [openclaw-integration.md](openclaw-integration.md)
- [openclaw-attach-quickstart.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/openclaw-attach-quickstart.md)
- [operator-observability.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/operator-observability.md)
- [raw-workspace-migration.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/raw-workspace-migration.md)
