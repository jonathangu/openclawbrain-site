# Reproduce Evaluation + Figures (Canonical)

This is the single source of truth for reproducing evaluation metrics and figures referenced on the OpenClawBrain site and paper.

## 1) Run the workflow-proof harness (deterministic, OpenClaw-shaped)

Use this harness for the current top-of-page proof slice on the homepage.

```bash
cd /path/to/openclawbrain
python3 -m examples.eval.simulate_openclaw_workflows \
  --output-dir scratch/workflow-proof/latest
```

Expected artifacts in `scratch/workflow-proof/latest/`:
- `workflow_state.json`
- `train_traces.jsonl`
- `train_labels.jsonl`
- `eval_queries.jsonl`
- `learning_curve.csv`
- `baseline_eval/summary.json`
- `report.md`
- `worked_example.md`

Current deterministic metrics:

| Mode | Exact target success | Required-node coverage |
| --- | ---: | ---: |
| `vector_topk` | 0.00 | 0.00 |
| `pointer_chase` | 0.25 | 0.38 |
| `graph_prior_only` | 0.50 | 0.50 |
| `learned` | 1.00 | 1.00 |

Interpretation:
- Cold-start graph priors are already somewhat useful on these held-out workflow-shaped queries.
- Async supervision trains a better learned runtime route policy than vector top-k, pointer chasing, or graph priors alone.

Non-claims:
- This is not a live production OpenClaw eval.
- This does not yet prove downstream answer quality directly; it proves retrieval-routing quality on deterministic workflow-shaped tasks.

## 2) Run the baseline + ablation harness (real query set)

Use the evaluation harness in the main `openclawbrain` code repo.

```bash
cd /path/to/openclawbrain
python examples/eval/run_eval.py \
  --state /path/to/state.json \
  --queries /path/to/queries.jsonl \
  --modes vector_only,edge_sim_legacy,graph_prior_only,qtsim_only,learned \
  --output /tmp/ocb_eval.json \
  --print-per-query
```

Expected output:
- `/tmp/ocb_eval.json` (per-mode summaries + optional per-query rows)

Baseline mapping used in the paper/blog:
- **Vector top-k** → `vector_only`
- **Top-k + reranker** → `edge_sim_legacy` (deterministic `route_mode=edge+sim` rerank)
- **Pointer-chasing** → `edge_sim_legacy` with multi-hop traversal enabled (default in the harness)

If you add a dedicated pointer-chasing mode in the harness, include it in `--modes` and document it in the report.

## 3) Run synthetic simulations (reward/accuracy/oracle-gap curves)

```bash
cd /path/to/openclawbrain
python examples/eval/simulate_expert_regions.py --output-dir /tmp/ocb_expert_regions
python examples/eval/simulate_two_cluster_routing.py --output-dir /tmp/ocb_two_cluster
```

Expected outputs:
- `/tmp/ocb_expert_regions/simulation_curve.csv` (columns: `epoch,reward,accuracy,oracle_gap_fraction,...`)
- `/tmp/ocb_expert_regions/report.md`
- `/tmp/ocb_two_cluster/simulation_curve.csv` (columns: `epoch,ce_loss,cluster_accuracy,top1_accuracy`)
- `/tmp/ocb_two_cluster/report.md`

## 4) Generate site/paper figures from CSVs

From this website repo:

```bash
python3 scripts/plot_eval.py \
  --inputs /tmp/ocb_expert_regions /tmp/ocb_two_cluster \
  --out figures/eval
```

Expected outputs in `figures/eval/`:
- `reward_vs_epoch.svg` + `reward_vs_epoch.png`
- `accuracy_vs_epoch.svg` + `accuracy_vs_epoch.png`
- `oracle_gap_closed.svg` + `oracle_gap_closed.png`
- `alpha_router_conf_hist.svg` + `alpha_router_conf_hist.png` (if data present)
- `ablation_bar_chart.svg` + `ablation_bar_chart.png`

## 5) Paper table placeholders

If you do not have the outputs above, leave paper/blog tables as `TBD` and cite the exact command + output path you plan to fill (for example, `/tmp/ocb_eval.json` and `/tmp/ocb_expert_regions/simulation_curve.csv`).
