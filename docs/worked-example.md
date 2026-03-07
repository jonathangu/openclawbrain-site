# Worked Example: One OpenClaw Turn End to End

This page shows one realistic but generic OpenClaw turn wired through OpenClawBrain.

It is a concrete operator example, not a benchmark.

Default stack assumed here:

- local embedder: `BAAI/bge-large-en-v1.5`
- local async teacher: `Ollama qwen3.5:35b`

Companion docs:

- [docs/openclaw-integration.md](openclaw-integration.md)
- [docs/reproduce-eval.md](reproduce-eval.md)
- [/proof/](../proof/)

How this page relates to the published proof families:

- this page is the minimum artifact contract for one real OpenClaw-shaped turn
- the deterministic workflow proof on `/proof/` is a separate mechanism bundle (evidence that the internals work correctly) built from 4 fixed workflow scenarios
- its scenario-level evidence matrix is `per_query_matrix.csv` and `per_query_matrix.md`: 16 rows showing, for each query and retrieval mode, exactly which knowledge-graph nodes made it into the prompt context
- recorded-session and sparse-feedback benchmark bundles scale from one turn contract to fixed multi-query and multi-seed comparisons
- none of these artifacts, by themselves, prove live production answer quality on served OpenClaw traffic

## Scenario

An OpenClaw operator is preparing a deploy note and asks:

> "For this billing banner patch, what deploy constraints should I mention?"

OpenClaw should not pass the raw user message into the brain unchanged. It should pass a stable summary plus a stable `turn_id`.

Example turn payload:

```text
turn_id: oc-main-2026-03-06-deploy-0142
summary: deploy note for billing banner patch; need freeze window, rollback owner requirement, and when support contact is required
```

Important detail:

- `turn_id` must stay stable across the compile call, later correction capture, and any learner outcome for this turn
- the summary should be compact and operator-meaningful, not a full prompt dump

## 1. OpenClaw activates a compiled context block

```ts
import { activate } from "@openclawbrain/activation";
import { compile }  from "@openclawbrain/compiler";

const turnId  = "oc-main-2026-03-06-deploy-0142";
const summary = "deploy note for billing banner patch; " +
                "need freeze window, rollback owner requirement, " +
                "and when support contact is required";

const candidates = activate(state, { summary, turnId });
const compiled    = compile(candidates, {
  format: "prompt",
  maxPromptContextChars: 20_000,
});
```

What to save for proof:

- exact activation + compile call parameters
- `turn_id`
- state path or state snapshot identifier

## 2. The compiler returns a bounded context block

Example prompt block returned to OpenClaw:

```text
[COMPILED_CONTEXT v1]
- Deploy policy snapshot: customer-visible changes freeze after 16:00 PT unless the on-call lead approves an exception.
- Release note rule: always name a rollback owner. Add a support contact only for customer-visible patches.
- Prior correction from this workspace: do not describe finance-impacting changes as auto-approved; they still need manual review.
[/COMPILED_CONTEXT]
```

What matters here:

- the returned block is bounded
- OpenClaw appends the block to its prompt
- raw retrieval internals are not injected into the prompt

This is the hot path. No async teacher call belongs here.

## 3. The model answer still happens in OpenClaw

The brain does not author the final reply. OpenClaw's model does.

Example OpenClaw answer:

```text
For this patch, mention the current freeze window, name a rollback owner, and include a support contact if the patch is customer-visible. If finance-impacting review is still involved, do not call it auto-approved.
```

Operator point:

- the current turn benefits from the returned context immediately
- the answer is still produced by the normal OpenClaw model path

## 4. Same-turn correction capture and learner outcome

Suppose the user immediately corrects the agent:

> "This patch is internal-only. Keep the rollback owner, but do not require a support contact."

Capture the correction against the same `turn_id`:

```ts
import { emitCorrectionEvent } from "@openclawbrain/events";
import { recordOutcome }       from "@openclawbrain/learner";

emitCorrectionEvent(state, {
  turnId,
  kind: "CORRECTION",
  content: "For internal-only patches, keep the rollback owner " +
           "but do not require a support contact.",
  lookback: 1,
  messageId: "assistant-2026-03-06-0142",
});

recordOutcome(state, {
  turnId,
  outcome: -1.0,
  lookback: 1,
});
```

What to save for proof:

- correction text
- `messageId`
- correction event output
- learner outcome output

What happens immediately:

- the correction and outcome are attached to the routing decision that was made for this `turn_id`
- OpenClaw can answer the correction in the conversation right away

What does **not** happen immediately:

- the current deployed `route_fn` is not magically replaced inline
- previous turns are not re-answered

## 5. Later replay, harvester, and maintain cycle

After the live conversation, run the background path on historical and newly captured sessions.

```bash
SESSIONS=~/.openclaw/agents/main/sessions

openclawbrain replay \
  --state "$STATE" \
  --sessions "$SESSIONS" \
  --fast-learning \
  --resume \
  --checkpoint ~/.openclawbrain/main/replay_checkpoint.json

openclawbrain harvest \
  --state "$STATE" \
  --events ~/.openclawbrain/main/learning_events.jsonl \
  --tasks split,merge,prune,connect,scale \
  --json

openclawbrain maintain \
  --state "$STATE" \
  --tasks health,decay,prune,merge \
  --json
```

This is where the correction joins the larger learning stream:

- replay mines the recorded session history
- harvester/scanner passes turn session events into learning signals
- maintenance applies structural cleanup and health tasks

Only after the updated state is deployed or cut over do later turns see the new routing behavior.

## 6. What changed now vs later

| Layer | Changes on this turn | Changes only after background learning and redeploy |
| --- | --- | --- |
| `turn_id` linkage | compile, correction capture, and outcome all refer to the same turn history | later analysis can replay the same turn history reliably |
| prompt context | OpenClaw gets the bounded compiled context block immediately | similar future turns may get a different block only after updated state is served |
| OpenClaw answer | the current answer can use the returned context right away | past answers do not retroactively change |
| correction record | the correction is stored immediately against the routing decision made for this turn | the correction influences future routing only after replay/harvest/update work is deployed |
| learned `route_fn` | current live weights stay as they were for this served state | later served weights can prefer better edges for similar deploy questions |
| graph structure | no need to block the live turn on structural work | split, merge, prune, connect, and decay effects appear after maintenance and cutover |

## 7. Minimum artifact bundle for one worked turn

If you want this turn to count as evidence instead of anecdote, keep at least:

- inbound summary and stable `turn_id`
- exact activation + compile parameters
- returned bounded compiled context block
- OpenClaw answer text or response trace id
- same-turn correction text plus correction event output
- learner outcome output
- later replay, harvest, and maintain commands plus output paths
- commit SHA and state identifier used for the turn and the later cutover

That bundle is the smallest useful proof unit for OpenClawBrain on real OpenClaw work.

## 8. The operational lesson

The concrete product story is:

1. OpenClaw can use the brain on the next turn.
2. Corrections can target the specific routing decision that was made for that query.
3. The router improves later, through background learning and a later deploy window.

That is the intended separation:

- immediate utility on the live turn
- continuous improvement off the hot path
- claims backed by saved artifacts instead of narrative certainty
