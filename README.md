# openclawbrain-site

Source for [openclawbrain.ai](https://openclawbrain.ai) — the public website for OpenClawBrain.

**OpenClawBrain** is a memory layer for OpenClaw agents that learns from corrections and picks better context.

Main package repo: [github.com/jonathangu/openclawbrain](https://github.com/jonathangu/openclawbrain)

---

## How the site works

Static HTML/CSS served via GitHub Pages with a custom domain (`openclawbrain.ai`). No build step, no framework, no bundler.

## Site map

| Path | Content |
|------|---------|
| `/` | Homepage |
| `/proof/` | Benchmark results and evidence |
| `/blog/` | Posts |
| `/learn/` | Conceptual explainers |
| `/docs/setup-guide/` | Developer setup |
| `/docs/worked-example/` | How It Works walkthrough |
| `/paper/` | Research paper |
| `/materials/` | Supplemental materials |

## Editing

```bash
git clone https://github.com/jonathangu/openclawbrain-site
# edit HTML files
git push origin main
```

GitHub Pages deploys automatically on push to `main`. Changes are live within a minute or two.

## Design

Dark theme, blue accents. Fonts: Inter, Crimson Pro, JetBrains Mono. CSS variables are defined at the top of `index.html` and shared across pages via `<style>` blocks — no separate stylesheet file.
