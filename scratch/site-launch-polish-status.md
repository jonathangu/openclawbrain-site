# Site Launch Polish Status

Date: 2026-03-06
Branch: `codex/20260306/site-launch-polish`

## Changes

- Added a canonical human-facing paper route at `/paper/` with direct PDF access, paper metadata, and supporting links.
- Repointed the homepage and proof surface from direct PDF links to `/paper/`, while keeping `/openclawbrain.pdf` as the direct artifact.
- Tightened cross-links across `/`, `/proof/`, `/blog/`, `/blog/v12.2.6-series/`, the current v12.2.6 blog pages, and `/materials/` so paper, proof, and blog navigation stay coherent.
- Kept the evidence boundary explicit: deterministic workflow proof is live now; recorded-session, shadow, and online proof still need future artifacts.

## Verification

- Served the repo locally on `127.0.0.1:8123`.
- Confirmed HTTP 200 for `/`, `/paper/`, `/proof/`, `/blog/`, `/materials/`, `/blog/v12.2.6-series/03-evaluation-ablations/`, and `/openclawbrain.pdf`.
- Ran a local cross-link check across the updated entry surfaces; it passed.
