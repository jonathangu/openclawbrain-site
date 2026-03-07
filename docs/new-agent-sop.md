# SOP: Create a new OpenClaw agent + dedicated OpenClawBrain profile (TypeScript-first)

Canonical flow for a new profile-style setup:

- one OpenClaw agent workspace
- one dedicated OpenClaw runtime brain profile
- one pinned OpenClawBrain package set
- explicit routing/binding in OpenClaw runtime

## A) Decide IDs and paths

```bash
agentId="pelican"
agentName="Pelican"
workspaceDir="$HOME/.openclaw/workspace-pelican"
```

Conventions:
- `agentId` is lowercase and stable (`main`, `pelican`, `bountiful`, ...)
- each agent has its own workspace
- each agent has its own OpenClaw brain profile

## B) Create workspace skeleton

```bash
mkdir -p "$workspaceDir/memory"

: > "$workspaceDir/AGENTS.md"
: > "$workspaceDir/SOUL.md"
: > "$workspaceDir/USER.md"
: > "$workspaceDir/MEMORY.md"
: > "$workspaceDir/IDENTITY.md"
: > "$workspaceDir/TOOLS.md"
: > "$workspaceDir/active-tasks.md"
: > "$workspaceDir/memory/$(date +%F).md"
```

Populate policy/persona files before live traffic.

## C) Build and verify OpenClawBrain package set

Run from the OpenClawBrain TypeScript workspace root:

```bash
corepack enable
pnpm install
pnpm check
pnpm release:pack
```

Promote one versioned pack set for this rollout.

## D) Add agent brain profile in OpenClaw runtime

Add a dedicated profile for this `agentId` with defaults on:

```json
{
  "agentId": "pelican",
  "brain": {
    "enabled": true,
    "packSet": "<versioned-pack-set>",
    "fastBootFromExistingFiles": true,
    "backgroundLearning": {
      "enabled": true,
      "prioritizeNewEvents": true
    },
    "labels": {
      "human": true,
      "self": true
    },
    "scanner": {
      "enabled": true
    },
    "harvest": {
      "enabled": true
    },
    "continuousGraphLearning": {
      "enabled": true,
      "decay": true,
      "hebbianCofiring": true,
      "structuralUpdates": true
    },
    "teacher": {
      "onHotPath": false
    }
  }
}
```

## E) Bind routing

Bind inbound channels to the new `agentId` in OpenClaw runtime config.

Minimum checks:
- new account/channel maps to `agentId`
- no overlap with existing agent bindings
- fail-open behavior retained for this route

## F) Add workspace policy snippet

Copy into `SOUL.md`:

```md
## Always-on memory policy (default)

- Treat clear user corrections as immediate labels.
- Treat durable user teachings as first-class labels.
- Keep human + self labels enabled.
- Keep scanner and harvest enabled.
- Keep teacher off the hot path.
- Never store secrets in workspace memory files.
```

## G) Verification checklist

Runtime checks:
- route reaches `agentId`
- first response works immediately from existing files
- background learning workers are active
- new events are prioritized over backlog
- labels/scanner/harvest loops are active
- continuous graph learning updates are visible

Boundary checks:
- OpenClaw owns serving/runtime/fail-open
- OpenClawBrain owns contracts, event/export normalization, provenance, packs, activation, compiler, learner

Proof checks:
- mechanism proof collected (contracts/provenance/normalization)
- product proof measured separately (quality/reliability outcomes)

## H) Common footguns

- sharing one workspace across multiple agents
- deploying mixed package revisions instead of one pack set
- disabling labels/scanner/harvest "temporarily" and forgetting to re-enable
- putting teacher logic on hot path
- claiming product gains from mechanism checks only
