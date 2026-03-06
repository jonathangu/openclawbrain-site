# SOP: Create a New OpenClaw Agent + Dedicated OpenClawBrain

Use this when you are creating a new OpenClaw agent and want the brain in the loop from the start.

Default stack assumed here:

- local embedder: `BAAI/bge-large-en-v1.5`
- local async teacher: `Ollama qwen3.5:35b`

## A. Decide IDs and paths

```bash
agentId="pelican"
agentName="Pelican"
workspaceDir="$HOME/.openclaw/workspace-pelican"
brainDir="$HOME/.openclawbrain/$agentId"
statePath="$brainDir/state.json"
```

Rules:

- one OpenClaw workspace per agent
- one dedicated brain per agent
- one daemon per brain

## B. Create the workspace skeleton

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

## C. Build the brain and use it immediately

```bash
mkdir -p "$brainDir"

openclawbrain init --workspace "$workspaceDir" --output "$brainDir"
openclawbrain doctor --state "$statePath"
openclawbrain serve --state "$statePath"
```

Smoke test:

```bash
python3 -m openclawbrain.openclaw_adapter.query_brain \
  "$statePath" \
  "what are this agent's standing rules?" \
  --chat-id smoke-test \
  --format prompt \
  --exclude-bootstrap
```

Do this before you schedule replay or harvesting. The first milestone is a working query path.

## D. Start the daemon in production

```bash
mkdir -p "$HOME/Library/LaunchAgents"

python3 -m openclawbrain.ops.write_launchd_plist \
  --agent-id "$agentId" \
  --state-path "$statePath" \
  --out-path "$HOME/Library/LaunchAgents/com.openclawbrain.${agentId}.plist" \
  --log-path "$HOME/.openclawbrain/${agentId}/daemon.log"

launchctl bootstrap "gui/$(id -u)" "$HOME/Library/LaunchAgents/com.openclawbrain.${agentId}.plist"
launchctl kickstart -k "gui/$(id -u)/com.openclawbrain.${agentId}"
launchctl print "gui/$(id -u)/com.openclawbrain.${agentId}"
```

## E. Bind the new agent in OpenClaw

```bash
python3 -m openclawbrain.ops.patch_openclaw_config \
  --agent-id "$agentId" \
  --agent-name "$agentName" \
  --workspace "$workspaceDir" \
  --telegram-account-id "$agentId" \
  --telegram-token-file "$HOME/.openclaw/tokens/telegram-${agentId}.token"
```

## F. Put the brain in `AGENTS.md`

```md
## OpenClawBrain

Before answering memory-sensitive turns:
python3 -m openclawbrain.openclaw_adapter.query_brain ~/.openclawbrain/<agentId>/state.json '<summary>' --chat-id '<chat_id>' --format prompt --exclude-bootstrap --max-prompt-context-chars 20000

For corrections:
python3 -m openclawbrain.openclaw_adapter.capture_feedback --state ~/.openclawbrain/<agentId>/state.json --chat-id '<chat_id>' --kind CORRECTION --content '<correction text>' --lookback 1 --message-id '<stable-message-id>' --json

For positive or negative outcomes:
python3 -m openclawbrain.openclaw_adapter.learn_by_chat_id --state ~/.openclawbrain/<agentId>/state.json --chat-id '<chat_id>' --outcome 1.0 --lookback 1 --json
```

## G. Turn on background learning

Historical replay:

```bash
openclawbrain replay \
  --state "$statePath" \
  --sessions "$HOME/.openclaw/agents/$agentId/sessions" \
  --fast-learning \
  --resume \
  --checkpoint "$brainDir/replay_checkpoint.json"
```

Harvest the replay output:

```bash
openclawbrain harvest \
  --state "$statePath" \
  --events "$brainDir/learning_events.jsonl" \
  --tasks split,merge,prune,connect,scale \
  --json
```

This is the intended order:

1. make the brain usable immediately
2. wire it into OpenClaw
3. replay history
4. keep training in the background

## H. Verification checklist

- `openclawbrain status --state "$statePath"` shows a running daemon
- `query_brain` returns a bounded `[BRAIN_CONTEXT]` block
- OpenClaw still works if the brain path is disabled
- the new agent can accept feedback with the same `chat_id`

## I. Operator policy to copy into `SOUL.md`

```md
## Always-on self-learning

- Treat clear user corrections as immediate memory updates.
- Use `capture_feedback --kind CORRECTION` in the same turn with the current `chat_id`.
- Use `learn_by_chat_id` for clear good or bad outcomes.
- Keep prompts tight: append bounded `[BRAIN_CONTEXT]`, not raw retrieval internals.
- Never log secrets or sensitive values into memory.
- Keep the async teacher off the hot path.
```

## J. What this setup is trying to achieve

The point of this SOP is not just "make a new memory file."

It is to set up the full OpenClawBrain loop correctly from the start:

- OpenClaw uses the brain right away
- the brain learns continuously in the background
- the learned runtime `route_fn` improves from real agent work over time
