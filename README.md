# openclawbrain.ai

Source for [openclawbrain.ai](https://openclawbrain.ai) — the public explainer site for **ocbrain**, a local, self-improving knowledge brain for AI agents.

This is a static site. It should answer:

- What is ocbrain?
- Why should I trust it?
- How does it actually work?

The site itself has no runtime logic and does not run ocbrain. It's a set of static HTML pages describing the project — the evidence-to-knowledge pipeline, the automatic safeguards, and the promotion rules — for anyone deciding whether to install it.

## Pages

- `/` — overview and current installed shape
- `/how-it-works/` — the evidence-to-knowledge-to-memory pipeline and the autopilot loop
- `/proof/` — the automatic safeguards and what ocbrain does not do
- `/agent-manual/` — orientation for an agent using ocbrain's MCP tools
- `/guide/` — a longer walkthrough of the data model and design
- `/install/` — install instructions

## Deploy

Static site, deployed via Cloudflare on push to `main`. No build step.

## Code and technical detail

- Code and README: [github.com/jonathangu/ocbrain](https://github.com/jonathangu/ocbrain)
- Architecture reference: `docs/ARCHITECTURE.md` in that repo
