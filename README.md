# openclawbrain.ai

Source for [openclawbrain.ai](https://openclawbrain.ai), the canonical public
operator and product documentation for
[ocbrain](https://github.com/jonathangu/ocbrain).

The site's first job is practical: help someone install, archive-first migrate,
and verify one event-authoritative local core across ChatGPT/Codex, Claude Code,
and OpenClaw. The explanation, proof, and agent contract support that job
without crowding the front door.

## Pages

- `/install/` — install, connect every runtime, archive-first migrate v0.x,
  activate explicitly, verify real tool use, and upgrade safely.
- `/how-it-works/` — the v1 event authority, Shared Context, exact source
  expansion, action/outcome receipts, and optional companion packages.
- `/proof/` — dated source, migration, runtime, and model-quality evidence,
  safeguards, and open risks.
- `/agent-manual/` — the current MCP operating contract.
- `/guide/` — the plain-language argument for the architecture.
- `/` — the product front door and route into those pages.

## Editorial contract

- Open with the idea already moving. Do not add scene-setting or autobiography.
- Use full sentences with visible reasoning and short landings where they help.
- Prefer clarity over compression.
- Use bullets for genuine enumeration and keep tables small enough to read on a
  phone.
- Date volatile numbers.
- Distinguish a unique win from a tie, a pipeline pass from a model pass, and a
  configured integration from a model-driven tool-use proof.
- Keep candidate construction, provisional pointer activation, fresh-client
  acceptance, and retain-or-rollback as separate claims. Migration never
  activates a candidate.
- Name the eight runtime MCP tools exactly. The admin profile adds only local
  preview, egress preview, correction, proposal listing/decision, and tombstone
  controls; never document hosted judgment, training, scheduler, or watchdog
  tools as part of core MCP.
- Describe `brain_events` as the semantic authority and projections/search
  features as rebuildable. Keep `ocbrain-training` and `ocbrain-ops` optional
  and physically separate from the core.
- Keep install, upgrade, and verify first on this domain.

## Development and deploy

The site is static HTML and CSS with no build step. Serve it locally from the
repository root:

```bash
python3 -m http.server 8000
```

GitHub Pages publishes the production site from `main`; Cloudflare fronts the
custom domain. Validate the HTML, internal
links, responsive layout, and live URLs before calling a change published.
