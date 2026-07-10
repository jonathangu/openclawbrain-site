# openclawbrain.ai

Source for [openclawbrain.ai](https://openclawbrain.ai), the canonical public
operator and product documentation for
[ocbrain](https://github.com/jonathangu/ocbrain).

The site's first job is practical: help someone install, upgrade, and verify one
local brain across ChatGPT/Codex, Claude Code, and OpenClaw. The explanation,
proof, and agent contract support that job without crowding the front door.

## Pages

- `/install/` — install, connect every runtime, verify real tool use, and
  upgrade without replacing the database.
- `/how-it-works/` — evidence, knowledge, labels, memory, datasets, and the
  light/heavy autopilot.
- `/proof/` — dated source/runtime evidence, the failed first model-quality
  result, safeguards, and open risks.
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
- Keep install, upgrade, and verify first on this domain.

## Development and deploy

The site is static HTML and CSS with no build step. Serve it locally from the
repository root:

```bash
python3 -m http.server 8000
```

Cloudflare deploys the production site from `main`. Validate the HTML, internal
links, responsive layout, and live URLs before calling a change published.
