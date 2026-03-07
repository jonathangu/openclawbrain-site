# Getting Started with OpenClawBrain

OpenClawBrain replaces static retrieval with a learned routing function (`route_fn`) over a knowledge graph. Instead of dumping the nearest text chunks into the prompt, it picks the right context for each query, learns from corrections and feedback, and gets sharper over time. It works alongside [OpenClaw](https://github.com/jonathangu/openclaw), which owns the runtime (sessions, tools, prompts, answers).

This guide gets you from zero to a working setup.

## What you need

- Node.js 20+ with `corepack`
- An OpenClaw runtime deployment (OpenClawBrain is a learning layer, not a standalone runtime)
- Workspace files (markdown, docs, memory files) for your agent to learn from
- API keys for your LLM provider(s), stored in OpenClaw's secrets config

## 1. Build the workspace

```bash
corepack enable
pnpm install
pnpm check            # type-check, lint, test, and verify package integrity
pnpm release:pack     # produce a versioned brain pack
```

A **brain pack** is a versioned bundle of context blocks (nodes from the knowledge graph) and learned routing weights. It is the artifact OpenClaw loads at runtime so that `route_fn` can decide what context to surface for a given query.

## 2. Connect to OpenClaw

OpenClaw owns runtime orchestration. You tell it where to find the brain pack by setting a runtime profile:

```json
{
  "brain": {
    "enabled": true,
    "packSet": "<versioned-pack-set>",       // which brain pack version to load
    "fastBootFromExistingFiles": true,        // start serving immediately from existing files
    "backgroundLearning": {
      "enabled": true,
      "prioritizeNewEvents": true             // learn from new usage before backfilling history
    },
    "labels": { "human": true, "self": true },// collect human and automated feedback signals
    "scanner": { "enabled": true },           // watch for new workspace and event data
    "harvest": { "enabled": true },           // extract learning signals from events
    "teacher": { "onHotPath": false }         // keep learning off the response path
  }
}
```

Key points:
- `fastBootFromExistingFiles` means OpenClaw starts serving immediately from your existing workspace files, even before background learning finishes processing history.
- `teacher.onHotPath: false` keeps learning off the serving path. Learning never slows down responses.
- Labels, scanner, and harvest are on by default to collect feedback and usage signals.

## 3. Confirm it is working

After connecting, verify these behaviors:

1. **Agent responds immediately.** OpenClaw boots from existing files without waiting for learning to complete.
2. **Background learning is running.** New events are learned first; historical backfill continues in the background.
3. **Fail-open works.** If the brain becomes unavailable or learning processes are delayed, OpenClaw still serves responses normally. The agent keeps working without brain-enhanced context.

## 4. Rollback and fail-open

OpenClaw owns fail-open behavior. If something goes wrong:

- **Brain becomes unavailable:** OpenClaw automatically falls back to core runtime behavior. Responses continue without brain-enhanced context.
- **Bad brain pack:** Roll back to the previous active pack set. Compilation from a given pack is deterministic, so rollback is safe.
- **Learning delays:** Scanner, harvest, and learner workers run asynchronously. Delays do not affect the hot path.

Recovery happens through background loops and pack rollback &mdash; no manual intervention required for fail-open.

## Next steps

- [Integration docs](openclaw-integration.md) &mdash; detailed runtime wiring and failure semantics
- [Reproduce benchmarks](reproduce-eval.md) &mdash; run the evaluation harness yourself
- [Proof package](/proof/) &mdash; worked examples and benchmark evidence
