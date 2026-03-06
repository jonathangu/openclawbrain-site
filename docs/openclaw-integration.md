# OpenClaw Integration

OpenClawBrain is built for ongoing OpenClaw use, not as a disconnected research demo.

The recommended integration pattern is:

1. start using the brain immediately from the workspace
2. keep the query path local and bounded
3. keep training in the background from historical and ongoing sessions
4. let the learned runtime `route_fn` serve future turns

Default stack assumed on this page:

- local embedder: `BAAI/bge-large-en-v1.5`
- local async teacher: `Ollama qwen3.5:35b`

Primary companion docs:

- [docs/setup-guide.md](setup-guide.md)
- [docs/operator-guide.md](operator-guide.md)
- [docs/worked-example.md](worked-example.md)
- [docs/reproduce-eval.md](reproduce-eval.md)
- [docs/new-agent-sop.md](new-agent-sop.md)

## What "brain-first" means

Brain-first mode does **not** replace OpenClaw.

It adds one memory-routing step before response generation:

```text
user message
  -> OpenClaw
  -> query_brain(summary, chat_id)
  -> bounded [BRAIN_CONTEXT]
  -> model response
  -> capture feedback / learn by chat_id
```

The important detail is what does **not** happen:

- no async teacher call on the hot path
- no unbounded prompt dump
- no requirement to finish replay or harvesting before first use

Concrete turn trace:

- [docs/worked-example.md](worked-example.md)

## Why this is the recommended path

OpenClaw users want memory that works while the agent is already running.

OpenClawBrain is designed around that operational reality:

- query-time routing stays local and fast
- feedback stays connected to real sessions via `chat_id`
- historical replay can happen after the first install
- continuous learning improves the runtime router over time

## Keep one canonical turn artifact bundle

For rollout proof, save at least one real or recorded OpenClaw turn end to end:

- inbound turn summary plus stable `chat_id`
- exact `query_brain` command and the bounded `[BRAIN_CONTEXT]` it returned
- the OpenClaw answer or response trace id
- same-turn `capture_feedback` and `learn_by_chat_id` JSON, if correction or outcome happened
- later replay, harvest, and maintain commands plus the state or commit used for the next cutover

That bundle is the minimum operator proof that the integration is real.

Worked example:

- [docs/worked-example.md](worked-example.md)

## 15-minute rollout

### 1. Build the brain

```bash
WORKSPACE=~/.openclaw/workspace
BRAIN_DIR=~/.openclawbrain/main

mkdir -p "$BRAIN_DIR"

openclawbrain init --workspace "$WORKSPACE" --output "$BRAIN_DIR"
openclawbrain doctor --state "$BRAIN_DIR/state.json"
```

### 2. Start the daemon

```bash
openclawbrain serve --state "$BRAIN_DIR/state.json"
openclawbrain status --state "$BRAIN_DIR/state.json"
```

### 3. Wire OpenClaw to query it

Recommended: enable the hook pack.

```bash
openclaw hooks install /path/to/openclawbrain/integrations/openclaw/hooks/openclawbrain-context-injector
openclaw hooks enable openclawbrain-context-injector
openclaw gateway restart
```

If you cannot use the hook pack yet, add the adapter calls manually in `AGENTS.md`.

```md
## OpenClawBrain

Before answering relevant turns:
python3 -m openclawbrain.openclaw_adapter.query_brain "$STATE" "$SUMMARY" --chat-id "$CHAT_ID" --format prompt --exclude-bootstrap --max-prompt-context-chars 20000

For corrections:
python3 -m openclawbrain.openclaw_adapter.capture_feedback --state "$STATE" --chat-id "$CHAT_ID" --kind CORRECTION --content "$CORRECTION_TEXT" --lookback 1 --message-id "$MESSAGE_ID" --json

For good or bad outcomes:
python3 -m openclawbrain.openclaw_adapter.learn_by_chat_id --state "$STATE" --chat-id "$CHAT_ID" --outcome 1.0 --lookback 1 --json
```

### 4. Query it once before touching the training loop

```bash
python3 -m openclawbrain.openclaw_adapter.query_brain \
  "$BRAIN_DIR/state.json" \
  "what are the current deploy constraints?" \
  --chat-id smoke-test \
  --format prompt \
  --exclude-bootstrap
```

This is the right order. First make sure the brain is actually in the loop. Then add replay and scheduled learning.

## What changes after brain-first is enabled

### Before

- OpenClaw answers from the currently loaded files and prompt structure.
- Memory improvements depend on manual context engineering or manual teach flows.
- Historical session knowledge is disconnected from live routing.

### After

- OpenClaw asks the brain for a bounded memory block before answering.
- Fired routes are tracked by `chat_id`, so corrections can target the route that actually fired.
- Replay, harvester passes, and async-teacher labeling improve the next runtime router.

## The runtime router is the product

OpenClawBrain's main claim is not "we store more memory."

The main claim is:

- the system learns a runtime `route_fn`
- that `route_fn` is served during live OpenClaw turns
- the labels for that policy come from multiple sources:
  - human feedback
  - self-learning outcomes
  - scanner/harvester labels
  - async teacher labels

Ultimate Policy Gradient is the update rule that unifies those sources while keeping a clear authority ordering.

Human corrections must stay able to override weaker but more numerous labels.

## What should stay asynchronous

Keep these off the live request path:

- historical replay
- scanner / harvester passes
- teacher labeling
- structural updates such as split / merge / prune / connect

That lets the agent stay usable while the brain keeps training.

## Continuous training loop

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

### Harvest the replay artifacts

```bash
openclawbrain harvest \
  --state "$BRAIN_DIR/state.json" \
  --events "$BRAIN_DIR/learning_events.jsonl" \
  --tasks split,merge,prune,connect,scale \
  --json
```

### Run maintenance

```bash
openclawbrain maintain \
  --state "$BRAIN_DIR/state.json" \
  --tasks health,decay,prune,merge \
  --json
```

Practical cadence:

- use the brain immediately after `init`
- replay historical sessions after the first successful rollout
- keep replay, harvest, and maintenance on a schedule for ongoing sessions

## Guardrails

- keep the integration fail-open: if the brain query fails, OpenClaw continues normally
- pass a stable `chat_id` on every relevant turn
- keep `--exclude-bootstrap` enabled so you do not duplicate files OpenClaw already injects
- append only bounded prompt context, not raw retrieval internals
- keep secrets and sensitive paths out of retrieval inputs

## Safe defaults for OpenClaw

| Setting | Recommended default |
| --- | --- |
| `query_brain` output | `--format prompt` |
| prompt budget | `--max-prompt-context-chars 20000` to start |
| duplication control | `--exclude-bootstrap` |
| live availability | fail-open if daemon or query path fails |
| feedback path | same-turn `capture_feedback` and `learn_by_chat_id` keyed by `chat_id` |
| initial training | historical replay after the first working query |

## What success looks like

You are in the right shape when:

- `openclawbrain status --state "$BRAIN_DIR/state.json"` shows a running daemon
- `query_brain` returns a bounded `[BRAIN_CONTEXT]` block
- OpenClaw can still answer normally if the brain path is disabled
- historical replay can run without interrupting the live agent
- corrections and outcomes are tied back to the same `chat_id`

## What is proven now vs what still needs proof

Proven now:

- the mechanism can be reproduced locally
- the site and paper can point to deterministic simulation and ablation artifacts
- the evaluation harness can compare routing modes on recorded query sets

Still needed for strong product claims:

- offline head-to-head eval on recorded OpenClaw sessions
- shadow-mode comparisons on real traffic
- limited online rollout with success, correction, latency, and cost tracking

That proof path is the canonical one:

- [docs/worked-example.md](worked-example.md)
- [docs/reproduce-eval.md](reproduce-eval.md)

## Next docs

- [docs/setup-guide.md](setup-guide.md)
- [docs/operator-guide.md](operator-guide.md)
- [docs/new-agent-sop.md](new-agent-sop.md)
