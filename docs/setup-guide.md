> Canonical docs live in the main `openclawbrain` repo. This page is the site snapshot for operators.

# OpenClawBrain Setup Guide

OpenClawBrain should be useful before any long training job finishes.

Recommended order:

1. Build a brain from the OpenClaw workspace.
2. Start the daemon and query it immediately.
3. Wire it into OpenClaw.
4. Replay historical sessions.
5. Keep replay, harvest, and maintenance running in the background.

These docs assume the default local stack unless you intentionally switch it:

- local embedder: `BAAI/bge-large-en-v1.5`
- local async teacher: `Ollama qwen3.5:35b`

## Prerequisites

- Python 3.10+
- `python3 -m pip install openclawbrain`
- an OpenClaw workspace directory
- an OpenClaw sessions directory if you want historical replay on day one
- the local embedder and local teacher available in your environment if you are following the default stack

## Fast start: get a usable brain first

```bash
WORKSPACE=~/.openclaw/workspace
BRAIN_DIR=~/.openclawbrain/main

mkdir -p "$BRAIN_DIR"

openclawbrain init --workspace "$WORKSPACE" --output "$BRAIN_DIR"
openclawbrain doctor --state "$BRAIN_DIR/state.json"
openclawbrain serve --state "$BRAIN_DIR/state.json"

python3 -m openclawbrain.openclaw_adapter.query_brain \
  "$BRAIN_DIR/state.json" \
  "what matters for deploy approvals?" \
  --chat-id smoke-test \
  --format prompt \
  --exclude-bootstrap
```

What this gives you:

- a portable `state.json` built from the workspace
- a hot in-memory daemon for low-overhead queries
- a real `query_brain` path you can wire into OpenClaw immediately

The key point: you do **not** need to wait for historical replay, harvester passes, or teacher labeling before the brain is useful.

## What runs on the hot path

During a live OpenClaw turn, keep the path simple:

1. summarize the inbound turn
2. query the brain with a stable `chat_id`
3. append bounded `[BRAIN_CONTEXT]`
4. answer normally

The async teacher does not belong on this path. The runtime value comes from the learned `route_fn` that was trained earlier.

## Start continuous background learning

After the first successful query, turn on the slow path.

### Replay historical sessions

```bash
SESSIONS=~/.openclaw/agents/main/sessions

openclawbrain replay \
  --state "$BRAIN_DIR/state.json" \
  --sessions "$SESSIONS" \
  --fast-learning \
  --resume \
  --checkpoint "$BRAIN_DIR/replay_checkpoint.json"
```

Use replay to mine historical sessions without blocking first use.

### Harvest the replayed learning events

```bash
openclawbrain harvest \
  --state "$BRAIN_DIR/state.json" \
  --events "$BRAIN_DIR/learning_events.jsonl" \
  --tasks split,merge,prune,connect,scale \
  --json
```

The scanner/harvester layer is one of the label producers that matters. It turns replayed sessions into structured signals that can update the routing policy later.

### Keep maintenance on a schedule

```bash
openclawbrain maintain \
  --state "$BRAIN_DIR/state.json" \
  --tasks health,decay,prune,merge \
  --json
```

Typical operating shape:

- `replay --fast-learning` on new session data
- `harvest` after replay
- `maintain` on a regular schedule

## Same-turn learning for ongoing use

The brain improves faster when live usage and feedback are connected.

### Capture explicit corrections

```bash
python3 -m openclawbrain.openclaw_adapter.capture_feedback \
  --state "$BRAIN_DIR/state.json" \
  --chat-id "$CHAT_ID" \
  --kind CORRECTION \
  --content "$CORRECTION_TEXT" \
  --lookback 1 \
  --message-id "$MESSAGE_ID" \
  --json
```

### Capture positive or negative outcomes

```bash
python3 -m openclawbrain.openclaw_adapter.learn_by_chat_id \
  --state "$BRAIN_DIR/state.json" \
  --chat-id "$CHAT_ID" \
  --outcome 1.0 \
  --lookback 1 \
  --json
```

Human corrections remain the highest-authority signal. They should be able to override weaker but higher-volume labels.

## Why this is different from plain retrieval

OpenClawBrain is not just "vector search with more storage."

It is trying to learn a better runtime route policy:

- the runtime `route_fn` chooses graph edges during a live query
- the scanner/harvester layer produces labels from historical and ongoing sessions
- the async teacher produces additional labels off the hot path
- Ultimate Policy Gradient combines those sources into one update rule

That split is the product direction:

- fast start
- local hot path
- continuous background learning
- tighter OpenClaw integration

## Defaults that matter

| Area | Recommended default |
| --- | --- |
| local embedder | `BAAI/bge-large-en-v1.5` |
| async teacher | `Ollama qwen3.5:35b` |
| prompt append mode | `--format prompt` |
| OpenClaw integration | `query_brain` before answer, `capture_feedback` / `learn_by_chat_id` after answer |
| duplication control | keep `--exclude-bootstrap` enabled |
| replay safety | keep `--resume` and a checkpoint file |
| proof discipline | do not publish claims that are not backed by artifacts |

## Minimal OpenClaw wiring

If you are not ready for the hook pack yet, the minimum manual integration is:

```md
## OpenClawBrain

Before answering memory-sensitive turns:
python3 -m openclawbrain.openclaw_adapter.query_brain "$STATE" "$SUMMARY" --chat-id "$CHAT_ID" --format prompt --exclude-bootstrap

When the user corrects the agent:
python3 -m openclawbrain.openclaw_adapter.capture_feedback --state "$STATE" --chat-id "$CHAT_ID" --kind CORRECTION --content "$CORRECTION_TEXT" --lookback 1 --message-id "$MESSAGE_ID" --json
```

The more complete guide is:

- [docs/openclaw-integration.md](openclaw-integration.md)

## Common mistakes

- treating historical replay as a prerequisite for first use
- putting the async teacher on the live request path
- forgetting to pass a stable `chat_id`
- shoving raw retrieval JSON into the prompt instead of a bounded `[BRAIN_CONTEXT]` block
- claiming production wins from simulations alone

## Use these next

- [docs/openclaw-integration.md](openclaw-integration.md)
- [docs/operator-guide.md](operator-guide.md)
- [docs/reproduce-eval.md](reproduce-eval.md)
