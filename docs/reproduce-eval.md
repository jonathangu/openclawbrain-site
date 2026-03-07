# Reproduce Evaluation + Figures (Canonical)

This is the single source of truth for reproducing evaluation metrics and figures referenced on the OpenClawBrain site and paper.
Most workflows below are package-first artifact pipelines in the TypeScript workspace; the sparse-feedback multiseed proof family is reproduced from the `brain-ground-zero` proof harness repo.

## 0) Bootstrap the TypeScript workspace

All reproduction commands use the TypeScript-first package surface.

```bash
cd /path/to/openclawbrain
corepack enable
pnpm install
pnpm check
pnpm release:pack
```

## 1) Run the workflow-proof harness (deterministic mechanism proof)

Use this harness for the published top-of-page mechanism proof slice on the homepage.

```bash
cd /path/to/openclawbrain
pnpm run eval:workflow-proof -- \
  --output-dir scratch/workflow-proof/latest
```

Expected artifacts in `scratch/workflow-proof/latest/`:
- `workflow_snapshot.json`
- `train_traces.jsonl`
- `train_labels.jsonl`
- `eval_queries.jsonl`
- `learning_curve.csv`
- `baseline_eval/summary.json`
- `report.md`
- `worked_example.md`

Deterministic metrics from the published workflow-proof artifacts:

| Mode | Exact target success | Required-node coverage |
| --- | ---: | ---: |
| `vector_topk` | 0.00 | 0.00 |
| `pointer_chase` | 0.25 | 0.38 |
| `graph_prior_only` | 0.50 | 0.50 |
| `learned` | 1.00 | 1.00 |

Interpretation:
- Cold-start graph priors are already somewhat useful on these held-out workflow-shaped queries.
- Async supervision trains a better learned route policy than vector top-k, pointer chasing, or graph priors alone.

Non-claims:
- This is mechanism proof, not full product proof.
- This is not a live production OpenClaw runtime eval.
- This does not directly prove downstream answer quality; it proves retrieval-routing behavior on deterministic workflow-shaped tasks.

## 2) Recorded-session head-to-head benchmark

The first fair comparison layer: a frozen recorded-session query set, fixed state, and one rubric applied to all modes.

Public bundle: `proof-results/recorded_h2h_relational_drift_001` in [brain-ground-zero](https://github.com/jonathangu/brain-ground-zero) at commit `1c54302`.

Current recorded-session metrics:

| Mode | Accuracy |
| --- | ---: |
| `full_brain` | 0.975 |
| `vector_rag_rerank` (best baseline) | 0.89625 |

- 800 queries, 41 training steps, 8 baselines compared.
- Delta: +7.9 percentage points (`full_brain` vs `vector_rag_rerank`).

Interpretation:
- The full brain policy beats all 8 baselines on a frozen recorded-session query set with a fixed rubric.
- This is benchmark/recorded-session evidence, not a live production answer-quality claim.

Non-claims:
- This does not prove live production answer quality on served OpenClaw traffic.
- This does not prove shadow-mode or online rollout outcomes.
- The next rungs are shadow-mode and narrow online rollout.

## 3) Sparse-feedback 10-seed proof family

This is the next major benchmark family after recorded-session head-to-head: sparse supervision over fixed workloads and seeds.

Public bundle: `proof-results/sparse_feedback_10seed` in [brain-ground-zero](https://github.com/jonathangu/brain-ground-zero/tree/main/proof-results/sparse_feedback_10seed) (run date `2026-03-07`).

Published sparse-feedback metrics:

| Mode | Accuracy | Context/query | H2H vs `full_brain` |
| --- | ---: | ---: | ---: |
| `full_brain` | 91.96% | 1.00 | &mdash; |
| `vector_rag_rerank` (best RAG baseline) | 67.05% | 5.00 | 1-9-0 |

- Delta: +24.91 percentage points (`full_brain` vs best RAG baseline).
- Pairwise headline: `full_brain` vs `vector_rag_rerank` is 9-1-0 across 10 seeds.
- Sparse feedback condition: explicit correctness signals are sparse (approximately 19% effective feedback events in the published run).

Reproduce from the proof harness repo:

```bash
git clone https://github.com/jonathangu/brain-ground-zero.git
cd brain-ground-zero
./scripts/run_sparse_feedback_proof.sh
```

Expected sparse-feedback artifacts in `proof-results/sparse_feedback_10seed/`:
- `summary.json`
- `summary_table.csv` + `summary_table.md`
- `leaderboard.csv` + `leaderboard.md`
- `pairwise_accuracy_delta.csv` + `pairwise_accuracy_delta.md`
- `win_rate_matrix.csv` + `win_rate_matrix.md`
- `per_seed_breakdown.csv` + `per_seed_breakdown.md`
- `per_seed_accuracy_matrix.csv` + `per_seed_accuracy_matrix.md`
- `proof_digest.md`
- `worked_example_trace.md`
- `learning_curve.png`
- `seeds.json`

Interpretation:
- The full brain policy stays materially ahead under sparse feedback while using much less context per query than the strongest RAG baseline.
- This is fixed-workload benchmark evidence and should be reported as such.

Non-claims:
- This does not prove live production answer quality on served OpenClaw traffic.
- This does not prove shadow-mode or online rollout outcomes.
- Runtime ownership boundaries are unchanged: OpenClaw owns live runtime, OpenClawBrain owns memory/learning artifacts.

## 4) Run the baseline + ablation harness (real query set)

Use the evaluation package entrypoint in the main `openclawbrain` workspace.

```bash
cd /path/to/openclawbrain
pnpm run eval:baseline -- \
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

## 5) Run synthetic simulations (reward/accuracy/oracle-gap curves)

```bash
cd /path/to/openclawbrain
pnpm run eval:sim-expert-regions -- --output-dir /tmp/ocb_expert_regions
pnpm run eval:sim-two-cluster -- --output-dir /tmp/ocb_two_cluster
```

Expected outputs:
- `/tmp/ocb_expert_regions/simulation_curve.csv` (columns: `epoch,reward,accuracy,oracle_gap_fraction,...`)
- `/tmp/ocb_expert_regions/report.md`
- `/tmp/ocb_two_cluster/simulation_curve.csv` (columns: `epoch,ce_loss,cluster_accuracy,top1_accuracy`)
- `/tmp/ocb_two_cluster/report.md`

## 6) Generate site/paper figures from CSVs

From this website repo:

```bash
cd /path/to/openclawbrain-site
pnpm run eval:plot -- \
  --inputs /tmp/ocb_expert_regions /tmp/ocb_two_cluster \
  --out figures/eval
```

Expected outputs in `figures/eval/`:
- `reward_vs_epoch.svg` + `reward_vs_epoch.png`
- `accuracy_vs_epoch.svg` + `accuracy_vs_epoch.png`
- `oracle_gap_closed.svg` + `oracle_gap_closed.png`
- `alpha_router_conf_hist.svg` + `alpha_router_conf_hist.png` (if data present)
- `ablation_bar_chart.svg` + `ablation_bar_chart.png`

## 7) Paper table placeholders

If a run does not produce the outputs above, leave paper/blog tables as `TBD` and cite the exact command + output path for the missing artifact (for example, `/tmp/ocb_eval.json` and `/tmp/ocb_expert_regions/simulation_curve.csv`).
