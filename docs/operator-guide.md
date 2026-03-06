# OpenClawBrain Operator Guide

This guide is for the day-2 question: once OpenClawBrain is integrated, what should stay running and what should be scheduled?

Default stack assumed here:

- local embedder: `BAAI/bge-large-en-v1.5`
- local async teacher: `Ollama qwen3.5:35b`

## 1. What should be on all the time

### Daemon

```bash
openclawbrain serve --state ~/.openclawbrain/main/state.json
```

### Health checks

```bash
openclawbrain status --state ~/.openclawbrain/main/state.json
openclawbrain doctor --state ~/.openclawbrain/main/state.json
openclawbrain info --state ~/.openclawbrain/main/state.json
```

Healthy shape:

- the daemon socket exists
- the brain answers `query_brain` requests quickly
- `doctor` and `info` do not show obvious corruption or drift

## 2. What should run in the background

### Replay new session data

```bash
openclawbrain replay \
  --state ~/.openclawbrain/main/state.json \
  --sessions ~/.openclaw/agents/main/sessions \
  --fast-learning \
  --resume \
  --checkpoint ~/.openclawbrain/main/replay_checkpoint.json
```

### Harvest replay output

```bash
openclawbrain harvest \
  --state ~/.openclawbrain/main/state.json \
  --events ~/.openclawbrain/main/learning_events.jsonl \
  --tasks split,merge,prune,connect,scale \
  --json
```

### Maintain graph health

```bash
openclawbrain maintain \
  --state ~/.openclawbrain/main/state.json \
  --tasks health,decay,prune,merge \
  --json
```

Recommended cadence:

- replay after new session batches
- harvest after replay
- maintain on a regular schedule

## 3. What should stay off the hot path

Do not put these in the live OpenClaw request path:

- historical replay
- scanner / harvester processing
- async teacher labeling
- heavy structural updates

The live request path should stay:

1. summarize the turn
2. `query_brain`
3. append bounded `[BRAIN_CONTEXT]`
4. answer
5. capture feedback

## 4. Why the learned route policy matters operationally

The operator goal is not "more memory files."

The operator goal is:

- the runtime `route_fn` gets better over time
- the labels for that policy come from real OpenClaw work
- the hot path stays local while training happens asynchronously

Ultimate Policy Gradient is the policy update that combines:

- human feedback
- self-learning outcomes
- scanner / harvester labels
- async teacher labels

Human corrections stay highest authority.

## 5. Rebuild and cutover

Use a quick replay on the current state when you need small improvements fast.

```bash
openclawbrain replay \
  --state ~/.openclawbrain/main/state.json \
  --sessions ~/.openclaw/agents/main/sessions \
  --fast-learning \
  --resume \
  --checkpoint ~/.openclawbrain/main/replay_checkpoint.json
```

Use rebuild-then-cutover when you want stronger single-writer hygiene.

```bash
examples/ops/rebuild_then_cutover.sh main ~/.openclaw/workspace ~/.openclaw/agents/main/sessions
```

## 6. Troubleshooting

| Symptom | Likely cause | Action |
| --- | --- | --- |
| `status` says the daemon is not running | service not started or wrong state path | start `openclawbrain serve` with the intended `--state` |
| `query_brain` is slow | daemon not used, wrong socket path, or state reload on each call | confirm the daemon is running and the adapter is using the same state |
| replay starts from old work | checkpoint missing or not used | add `--resume --checkpoint ~/.openclawbrain/main/replay_checkpoint.json` |
| corrections do not target recent routes | missing or unstable `chat_id` | pass the same `chat_id` through query and feedback |
| the brain is in the prompt twice | bootstrap files were already injected by OpenClaw | keep `--exclude-bootstrap` enabled |

## 7. The proof discipline operators should keep

Use three layers of evidence:

1. local reproducibility for the mechanism
2. offline head-to-head on recorded OpenClaw sessions
3. shadow traffic and narrow online rollout

Do not skip from simulations straight to broad product claims.

Canonical proof path:

- [docs/reproduce-eval.md](reproduce-eval.md)

## 8. Use these next

- [docs/openclaw-integration.md](openclaw-integration.md)
- [docs/setup-guide.md](setup-guide.md)
- [docs/new-agent-sop.md](new-agent-sop.md)
