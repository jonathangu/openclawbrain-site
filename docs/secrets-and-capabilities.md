# Secrets and Capabilities Registry

This is the canonical policy for secrets in OpenClaw/OpenClawBrain workspaces.

## Policy

- Secret values must never be stored in memory notes, prompts, or OpenClawBrain state.
- Agents should only retain capability metadata and secret pointers.
- Pointers are allowed: env var names, `tokenFile` paths, and local file locations.
- Verification must be boolean only (present/missing), never value disclosure.

## Recommended local secret storage (Mac mini)

- Store secret values in `~/.openclaw/credentials/env/<project>.env` and set `chmod 600`.
- Keep each repo/workspace `.env` as a symlink to that centralized file so existing app/runtime loading still works.
- Keep token files in `~/.openclaw/credentials/*.token` and set `chmod 600`.
- Never write secret values into brain/workspace notes, prompts, or state.

Safe setup (no value printing):

```bash
mkdir -p ~/.openclaw/credentials/env ~/.openclaw/credentials

repo_dir=~/path/to/repo
project_env=~/.openclaw/credentials/env/<project>.env

# Backup and move an existing local .env into centralized storage.
if [ -f "$repo_dir/.env" ] && [ ! -L "$repo_dir/.env" ]; then
  cp "$repo_dir/.env" "$repo_dir/.env.backup.$(date +%Y%m%d%H%M%S)"
  mv "$repo_dir/.env" "$project_env"
fi

chmod 600 "$project_env"
[ -L "$repo_dir/.env" ] && rm "$repo_dir/.env"
ln -s "$project_env" "$repo_dir/.env"
chmod 600 ~/.openclaw/credentials/*.token 2>/dev/null || true
```

## Minimal Schema

Each registry entry should track:

- `service`: provider or system (for example, `Mapbox`).
- `capability`: what the secret enables.
- `required_keys`: required env var names.
- `storage_pointer`: local pointer (env file path, `tokenFile`, or equivalent).
- `verify`: boolean check only (no value output).
- `notes`: scope, rotation, and handling constraints.

## Canonical Capability Entries

### Mapbox

- `service`: `Mapbox`
- `capability`: maps, geocoding, tiles, routing
- `required_keys`: `VITE_MAPBOX_TOKEN`, `MAPBOX_API_KEY`, `MAPBOX_SECRET_TOKEN`
- `storage_pointer`: `.env*` key location or operator token file
- `verify`: key assignment is non-empty (`true/false`)
- `notes`: `VITE_MAPBOX_TOKEN` is public-facing; keep secret tokens server-side

### Perplexity

- `service`: `Perplexity`
- `capability`: web-grounded LLM search
- `required_keys`: `PPLX_API_KEY`
- `storage_pointer`: `.env*` key location
- `verify`: key assignment is non-empty (`true/false`)
- `notes`: rotate on exposure or permission changes

### Polygon

- `service`: `Polygon`
- `capability`: market data APIs
- `required_keys`: `POLYGON_API_KEY`
- `storage_pointer`: `.env*` key location
- `verify`: key assignment is non-empty (`true/false`)
- `notes`: scope to required market products

### NewsAPI

- `service`: `NewsAPI`
- `capability`: top-headlines and article search
- `required_keys`: `NEWSAPI_KEY`
- `storage_pointer`: `.env*` key location
- `verify`: key assignment is non-empty (`true/false`)
- `notes`: monitor plan limits and rotate when needed

### OpenAI

- `service`: `OpenAI`
- `capability`: embeddings + LLM calls
- `required_keys`: `OPENAI_API_KEY`
- `storage_pointer`: `.env*` key location
- `verify`: key assignment is non-empty (`true/false`)
- `notes`: used by the broader OpenClaw runtime if configured for OpenAI-based agent or tool paths. OpenClawBrain itself does not require this key — its default stack uses local BGE-large embeddings and a local Ollama teacher.

### SEC/EDGAR

- `service`: `SEC/EDGAR`
- `capability`: public filings access
- `required_keys`: none
- `storage_pointer`: not applicable
- `verify`: `true` (no key required)
- `notes`: follow fair-access/User-Agent guidelines

### ClinicalTrials.gov

- `service`: `ClinicalTrials.gov`
- `capability`: public clinical-trial registry queries
- `required_keys`: none
- `storage_pointer`: not applicable
- `verify`: `true` (no key required)
- `notes`: no key needed for standard public endpoints

### FDA open data

- `service`: `FDA open data`
- `capability`: OpenFDA public datasets and search endpoints
- `required_keys`: none
- `storage_pointer`: not applicable
- `verify`: `true` (no key required)
- `notes`: no key needed for standard public endpoints

## Operations

Run pointer harvest and leak-audit jobs using the current OpenClawBrain TypeScript tooling for your workspace.

Required behavior:
- harvest outputs pointer-only rows (env key names, token file paths, file modes)
- secret values are never loaded into memory notes, prompt payloads, or state
- credential-file pointer harvest includes `~/.openclaw/credentials` by default unless explicitly disabled
- strict leak audit reports only path + line metadata for suspected leaks
