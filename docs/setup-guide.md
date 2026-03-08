> Canonical source: the public `openclawbrain` repo. This site page mirrors the current setup truth and links outward where the full repo docs are not mirrored here.

# Setup Guide

For the current `0.1.2` wave, there is one blessed external install lane: repo tip plus local `.release/*.tgz` tarballs.
The tagged + published npm lane stays future-only until `pnpm release:status` shows a tagged release candidate and the post-publish checks in `docs/release.md` pass in the public repo.

## Current repo-tip truth

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm release:status
pnpm release:check
```

That sequence keeps the current technical-alpha story honest:

- `pnpm release:status` shows the current ship surface and which launch-tier claim sets are actually honest now.
- `pnpm release:check` rebuilds the repo proof lane, refreshes `.release/*.tgz`, runs `pnpm fresh-env:smoke`, and writes `.release/release-proof-manifest.json`.
- `pnpm fresh-env:smoke` is the clean outside-consumer attach proof for the current repo-tip + tarball lane.
- `pnpm release:consumer:smoke` remains the narrower tarball-install-only check.

Do **not** tell external users to run bare `pnpm add @openclawbrain/*` yet.
That registry lane stays future-only until a later wave has a matching release tag on `HEAD`, the publish lane finishes, and post-publish checks pass.

## Start here on this site

1. [docs/openclaw-integration.md](openclaw-integration.md)
2. [docs/reproduce-eval.md](reproduce-eval.md)
3. [docs/worked-example.md](worked-example.md)
4. [proof package](/proof/)

## Canonical repo docs

Use the public repo for the docs that are not mirrored on this site:

1. [openclaw-attach-quickstart.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/openclaw-attach-quickstart.md)
2. [design-partner-operating-model.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/design-partner-operating-model.md)
3. [operator-observability.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/operator-observability.md)
4. [contracts-v1.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/contracts-v1.md)
5. [release.md](https://github.com/jonathangu/openclawbrain/blob/main/docs/release.md)

## Repo-local quick smoke

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm check
pnpm release:status
pnpm fresh-env:smoke
```

That local smoke is narrower than `pnpm release:check`: it is useful when you want the current proof lanes plus the clean-room attach proof without rerunning the full release packaging checklist.

## Claim boundary

- Current truthful surface: repo tip, local tarballs, promoted-pack compile, and the checked-in proof lanes.
- Supporting benchmark bundles for broader comparative and `QTsim` claims live separately in Brain Ground Zero.
- Shadow-mode, live-traffic, and post-publish npm-install claims stay future-only until matching artifacts exist.
