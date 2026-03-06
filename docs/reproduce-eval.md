# Prove It: Canonical Evaluation Path

This page is the contract for what OpenClawBrain can claim and how those claims should be proven.

The short version:

- simulations are useful for mechanism proof
- simulations alone are not enough for product proof
- strong claims need offline recorded-session eval, shadow traffic, and narrow online rollout

Smallest useful proof unit:

- one traceable turn with a stable `chat_id`, saved `query_brain` output, and any same-turn feedback artifacts
- canonical example: [docs/worked-example.md](worked-example.md)

## Evidence ladder

### 1. Mechanism proof: deterministic simulations

Use the simulation scripts to show that the routing and learning mechanism behaves as expected.

```bash
cd /path/to/openclawbrain
python examples/eval/simulate_expert_regions.py --output-dir /tmp/ocb_expert_regions
python examples/eval/simulate_two_cluster_routing.py --output-dir /tmp/ocb_two_cluster
```

What this proves:

- the learned route policy can improve in controlled settings
- the confidence gate and ablations behave as expected
- the figure-generation path is reproducible

What this does **not** prove:

- superiority on real OpenClaw traffic
- cost wins in production
- universal gains across one-off workloads

### Current workflow-proof slice used on `/proof/`

This is the deterministic mechanism bundle behind the current workflow-proof copy on the site.

```bash
cd /private/tmp/ocb-proof-sims
python3 -m examples.eval.simulate_openclaw_workflows \
  --output-dir scratch/workflow-proof/latest
```

Key generated files:

- `scratch/workflow-proof/latest/workflow_state.json`
- `scratch/workflow-proof/latest/train_traces.jsonl`
- `scratch/workflow-proof/latest/train_labels.jsonl`
- `scratch/workflow-proof/latest/eval_queries.jsonl`
- `scratch/workflow-proof/latest/learning_curve.csv`
- `scratch/workflow-proof/latest/baseline_eval/summary.csv`
- `scratch/workflow-proof/latest/baseline_eval/summary.json`
- `scratch/workflow-proof/latest/report.md`
- `scratch/workflow-proof/latest/per_query_matrix.csv`
- `scratch/workflow-proof/latest/per_query_matrix.md`
- `scratch/workflow-proof/latest/worked_example.md`

What the scenario-level matrix adds:

- `per_query_matrix.csv` and `per_query_matrix.md` flatten the workflow slice into 16 rows: 4 held-out scenarios x 4 retrieval modes
- each row records `query_id`, `scenario`, `category`, `required_node_ids`, `prompt_context_included_node_ids`, `target_success`, `required_node_coverage`, and `pointer_turns` when relevant
- `report.md` is the compact count table; `per_query_matrix.*` is the citable prompt-context evidence behind those totals

What this proves:

- cold-start graph priors can already recover the required prompt-context nodes on some fixed workflow queries
- async teacher supervision can improve the served learned `route_fn` later, off the hot path
- the deterministic harness makes the exact node IDs that reached prompt context inspectable per scenario

What this does **not** prove:

- downstream answer quality
- real OpenClaw task success or production superiority
- scanner/harvester label quality on live histories

## 2. Offline head-to-head: recorded queries or sessions

Run the harness on a fixed query set against the same state and the same evaluation rubric.

```bash
cd /path/to/openclawbrain
python examples/eval/run_eval.py \
  --state /path/to/state.json \
  --queries /path/to/queries.jsonl \
  --modes vector_only,edge_sim_legacy,graph_prior_only,qtsim_only,learned \
  --output /tmp/ocb_eval.json \
  --print-per-query
```

Baseline mapping used by the site:

- vector top-k -> `vector_only`
- deterministic rerank / legacy edge similarity -> `edge_sim_legacy`
- graph prior only -> `graph_prior_only`
- query-conditioned route component only -> `qtsim_only`
- learned runtime route policy -> `learned`

What this adds beyond simulations:

- same recorded workload across all modes
- same success criteria across all modes
- real state and real query artifacts

Minimum artifacts to keep:

- exact command
- commit SHA
- output JSON path
- query set path
- seed, if applicable

## 3. Shadow-mode proof: real OpenClaw traffic without serving it yet

Before making strong product claims, compare brain-off and brain-on on recorded or mirrored OpenClaw traffic.

Minimum requirements:

- same traffic slice
- same scoring rubric
- same output budget rules
- side-by-side artifact retention

Track at least:

- task success or correctness
- correction rate
- prompt size
- latency
- cost or token spend

This is the first step that starts to answer whether the learned runtime `route_fn` is helping the real OpenClaw workflow.

## Artifact checklist

Use this as the minimum retention policy for anything cited on the site.

| Evaluation type | Save at minimum |
| --- | --- |
| deterministic sim run | exact command, commit SHA, seed or config, output directory, and generated JSON/SVG/PNG artifacts |
| recorded-session eval | frozen query or session-set path plus digest, state path or snapshot identifier, rubric version, per-mode outputs, per-query judgments, and sampled turn bundles in the [worked-example format](worked-example.md) |
| shadow-mode comparison | traffic slice definition and dates, brain-off and brain-on outputs for the same turns, output-budget rules, prompt/latency/cost logs, and saved disagreement traces with `chat_id` plus bounded `[BRAIN_CONTEXT]` |

## 4. Narrow online rollout

Only after shadow-mode evidence exists:

- enable for a narrow slice of traffic
- keep fail-open behavior
- compare success, correction rate, prompt size, latency, and cost
- publish only the claims that the artifacts support

## Figure generation for the site

From this website repo:

```bash
python3 scripts/plot_eval.py \
  --inputs /tmp/ocb_expert_regions /tmp/ocb_two_cluster \
  --out figures/eval
```

Expected figure outputs:

- `figures/eval/reward_vs_epoch.svg`
- `figures/eval/accuracy_vs_epoch.svg`
- `figures/eval/oracle_gap_closed.svg`
- `figures/eval/alpha_router_conf_hist.svg`
- `figures/eval/ablation_bar_chart.svg`

Current workflow-proof figures used on `/proof/`:

```bash
python3 scripts/generate_workflow_proof_figures.py \
  --baseline /private/tmp/ocb-proof-sims/scratch/workflow-proof/latest/baseline_eval/summary.csv \
  --curve /private/tmp/ocb-proof-sims/scratch/workflow-proof/latest/learning_curve.csv \
  --outdir figures/eval
```

Current cited metrics from that artifact bundle:

- exact-target success: `vector_topk` 0/4, `pointer_chase` 1/4, `graph_prior_only` 2/4, `learned` 4/4
- graph prior stays flat at 2/4 across all 16 epochs
- learned first reaches 4/4 at epoch 14
- scenario summary source: `/private/tmp/ocb-proof-sims/scratch/workflow-proof/latest/report.md`
- scenario-level prompt-context evidence: `/private/tmp/ocb-proof-sims/scratch/workflow-proof/latest/per_query_matrix.csv` and `/private/tmp/ocb-proof-sims/scratch/workflow-proof/latest/per_query_matrix.md`
- worked retrieval example source: `/private/tmp/ocb-proof-sims/scratch/workflow-proof/latest/worked_example.md`

Expected workflow-proof outputs:

- `figures/eval/workflow_proof_exact_target_success.svg`
- `figures/eval/workflow_proof_learning_curve.svg`

These figures are still mechanism proof only. They make the current deterministic retrieval result concrete; they do not replace recorded-session, shadow, or online product evidence.

For the current workflow-proof slice, keep the claim boundary explicit:

- `report.md` and `per_query_matrix.*` show which memory nodes reached prompt context inside the sim
- they do **not** show downstream answer quality or production operator outcomes
- the product claim stays narrow: OpenClaw-native memory plus a learned runtime router on a local hot path, with async teacher supervision off that path

## Reporting contract

Use these labels consistently:

- `proven now` for deterministic local artifacts that exist
- `needs head-to-head` for claims that require recorded-session or shadow-mode evidence
- `not claimed` for anything without artifacts

If an artifact does not exist yet:

- leave the table cell as `TBD`
- cite the exact command and output path you intend to fill later

Do not backfill narrative certainty ahead of the evidence.
