#!/usr/bin/env python3
"""Generate evaluation figures from OpenClawBrain simulation CSV outputs.

Expected outputs in figures/eval/:
- reward_vs_epoch.svg
- accuracy_vs_epoch.svg
- oracle_gap_closed.svg
- alpha_router_conf_hist.svg (if data available; placeholder otherwise)
- ablation_bar_chart.svg (optional helper for paper Figure 3)
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np


def _norm(name: str) -> str:
    return "".join(ch for ch in name.lower() if ch.isalnum())


def _first_matching(headers: Sequence[str], candidates: Sequence[str]) -> Optional[str]:
    norm_to_header = {_norm(h): h for h in headers}
    for cand in candidates:
        key = _norm(cand)
        if key in norm_to_header:
            return norm_to_header[key]
    for h in headers:
        hn = _norm(h)
        for cand in candidates:
            if _norm(cand) in hn:
                return h
    return None


def _parse_float(value: str) -> Optional[float]:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return None
    if np.isnan(v) or np.isinf(v):
        return None
    return v


@dataclass
class Series:
    label: str
    x: np.ndarray
    y: np.ndarray


def _read_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        rows = [row for row in reader]
    return headers, rows


def _extract_series(
    path: Path,
    y_candidates: Sequence[str],
    x_candidates: Sequence[str] = ("epoch", "step", "iteration", "iter", "t", "time"),
) -> Optional[Series]:
    headers, rows = _read_csv(path)
    if not headers or not rows:
        return None
    return _extract_series_from_rows(headers, rows, y_candidates, x_candidates, default_label=path.stem.replace("_", " "))


def _extract_series_from_rows(
    headers: Sequence[str],
    rows: Sequence[Dict[str, str]],
    y_candidates: Sequence[str],
    x_candidates: Sequence[str] = ("epoch", "step", "iteration", "iter", "t", "time"),
    default_label: str = "",
) -> Optional[Series]:
    x_col = _first_matching(headers, x_candidates)
    y_col = _first_matching(headers, y_candidates)
    if not y_col:
        return None

    x_vals: List[float] = []
    y_vals: List[float] = []
    for idx, row in enumerate(rows):
        xv = _parse_float(row.get(x_col, "") if x_col else str(idx + 1))
        yv = _parse_float(row.get(y_col, ""))
        if yv is None:
            continue
        if xv is None:
            xv = float(idx + 1)
        x_vals.append(xv)
        y_vals.append(yv)

    if not x_vals:
        return None

    x = np.array(x_vals, dtype=float)
    y = np.array(y_vals, dtype=float)
    order = np.argsort(x)
    return Series(label=default_label, x=x[order], y=y[order])


def _extract_gap_closed(path: Path) -> Optional[Series]:
    headers, rows = _read_csv(path)
    if not headers or not rows:
        return None
    return _extract_gap_closed_from_rows(headers, rows, default_label=path.stem.replace("_", " "))


def _extract_gap_closed_from_rows(
    headers: Sequence[str],
    rows: Sequence[Dict[str, str]],
    default_label: str = "",
) -> Optional[Series]:

    x_col = _first_matching(headers, ("epoch", "step", "iteration", "iter", "t"))

    direct_col = _first_matching(
        headers,
        (
            "oracle_gap_closed",
            "gap_closed",
            "oracle_closed",
            "oracle_gap_closed_pct",
            "oracle_gap_closed_percent",
        ),
    )

    x_vals: List[float] = []
    y_vals: List[float] = []

    if direct_col:
        for idx, row in enumerate(rows):
            xv = _parse_float(row.get(x_col, "") if x_col else str(idx + 1))
            yv = _parse_float(row.get(direct_col, ""))
            if yv is None:
                continue
            if yv > 1.0:
                yv = yv / 100.0
            if xv is None:
                xv = float(idx + 1)
            x_vals.append(xv)
            y_vals.append(max(0.0, min(1.0, yv)))
    else:
        gap_col = _first_matching(headers, ("oracle_gap", "gap_to_oracle", "oracle_delta", "regret"))
        reward_col = _first_matching(headers, ("reward", "mean_reward", "avg_reward", "return"))
        oracle_reward_col = _first_matching(headers, ("oracle_reward", "best_possible_reward", "reward_oracle"))

        if gap_col:
            gaps: List[Tuple[float, float]] = []
            for idx, row in enumerate(rows):
                xv = _parse_float(row.get(x_col, "") if x_col else str(idx + 1))
                gv = _parse_float(row.get(gap_col, ""))
                if gv is None:
                    continue
                if xv is None:
                    xv = float(idx + 1)
                gaps.append((xv, gv))
            if gaps:
                init_gap = next((abs(g) for _, g in gaps if abs(g) > 1e-12), None)
                if init_gap:
                    x_vals = [x for x, _ in gaps]
                    y_vals = [max(0.0, min(1.0, 1.0 - (abs(g) / init_gap))) for _, g in gaps]
        elif reward_col and oracle_reward_col:
            for idx, row in enumerate(rows):
                xv = _parse_float(row.get(x_col, "") if x_col else str(idx + 1))
                rv = _parse_float(row.get(reward_col, ""))
                ov = _parse_float(row.get(oracle_reward_col, ""))
                if rv is None or ov is None or abs(ov) < 1e-12:
                    continue
                if xv is None:
                    xv = float(idx + 1)
                closed = max(0.0, min(1.0, rv / ov))
                x_vals.append(xv)
                y_vals.append(closed)

    if not x_vals:
        return None

    x = np.array(x_vals, dtype=float)
    y = np.array(y_vals, dtype=float)
    order = np.argsort(x)
    return Series(label=default_label, x=x[order], y=y[order])


def _extract_alpha_values(path: Path) -> Optional[np.ndarray]:
    headers, rows = _read_csv(path)
    if not headers or not rows:
        return None

    alpha_col = _first_matching(
        headers,
        (
            "alpha_router",
            "alpha",
            "router_alpha",
            "mix_alpha",
            "lambda",
            "confidence_mix",
        ),
    )
    if not alpha_col:
        return None

    values: List[float] = []
    for row in rows:
        val = _parse_float(row.get(alpha_col, ""))
        if val is None:
            continue
        values.append(max(0.0, min(1.0, val)))

    if not values:
        return None
    return np.array(values, dtype=float)


def _pick_label(path: Path) -> str:
    stem = path.stem.lower()
    if "expert" in stem or "region" in stem:
        return "expert-regions"
    if "cluster" in stem:
        return "two-cluster"
    return path.stem.replace("_", " ")


def _collect_csvs(input_dirs: Sequence[Path], explicit_csvs: Sequence[Path]) -> List[Path]:
    found = []
    for directory in input_dirs:
        if not directory.exists():
            continue
        found.extend(sorted(p for p in directory.rglob("*.csv") if p.is_file()))
    found.extend(explicit_csvs)
    unique: Dict[Path, None] = {}
    for p in found:
        unique[p.resolve()] = None
    return list(unique.keys())


def _setup_style() -> None:
    plt.style.use("seaborn-v0_8-whitegrid")
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "axes.titlesize": 13,
            "axes.labelsize": 11,
            "legend.fontsize": 9,
            "axes.edgecolor": "#2B3140",
            "grid.color": "#D9DFEA",
            "grid.alpha": 0.65,
        }
    )


def _save_plot(fig: plt.Figure, outpath: Path) -> None:
    outpath.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(outpath, format="svg", bbox_inches="tight")
    fig.savefig(outpath.with_suffix(".png"), format="png", dpi=220, bbox_inches="tight")
    plt.close(fig)


def _plot_line(
    series_list: Sequence[Series],
    outpath: Path,
    title: str,
    ylabel: str,
    y_lim: Optional[Tuple[float, float]] = None,
) -> None:
    fig, ax = plt.subplots(figsize=(8.4, 4.6), dpi=150)
    palette = ["#005A9C", "#E07A00", "#2A9D8F", "#7A5195", "#5F6F94", "#B95F89", "#3D8B5F"]

    if series_list:
        for idx, s in enumerate(series_list):
            color = palette[idx % len(palette)]
            ax.plot(s.x, s.y, linewidth=2.3, color=color, label=s.label)
        ax.legend(frameon=False, loc="best")
    else:
        ax.text(
            0.5,
            0.5,
            "No matching data found in provided CSV files",
            ha="center",
            va="center",
            fontsize=11,
            color="#495366",
            transform=ax.transAxes,
        )

    ax.set_title(title)
    ax.set_xlabel("Epoch")
    ax.set_ylabel(ylabel)
    if y_lim:
        ax.set_ylim(*y_lim)
    _save_plot(fig, outpath)


def _plot_hist(values: Optional[np.ndarray], outpath: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(7.2, 4.6), dpi=150)
    if values is None or values.size == 0:
        ax.text(
            0.5,
            0.5,
            "alpha_router column not found",
            ha="center",
            va="center",
            fontsize=11,
            color="#495366",
            transform=ax.transAxes,
        )
    else:
        ax.hist(values, bins=20, color="#005A9C", alpha=0.86, edgecolor="white")
        ax.set_xlim(0.0, 1.0)
    ax.set_title(title)
    ax.set_xlabel("alpha_router")
    ax.set_ylabel("Count")
    _save_plot(fig, outpath)


def _build_ablation_chart(csv_paths: Sequence[Path], outpath: Path) -> None:
    categories = ["vector_only", "graph_prior_only", "qtsim_only", "learned"]
    values: Dict[str, float] = {}

    for path in csv_paths:
        headers, rows = _read_csv(path)
        if not headers or not rows:
            continue
        variant_col = _first_matching(headers, ("variant", "setting", "arm", "ablation", "model"))
        score_col = _first_matching(headers, ("accuracy", "success", "reward", "score", "mean_reward"))
        if not variant_col or not score_col:
            continue
        for row in rows:
            variant_raw = (row.get(variant_col) or "").strip().lower()
            score = _parse_float(row.get(score_col, ""))
            if score is None:
                continue
            for cat in categories:
                if cat in variant_raw:
                    values[cat] = score

    fig, ax = plt.subplots(figsize=(8.0, 4.6), dpi=150)
    if values:
        ys = [values.get(cat, np.nan) for cat in categories]
        bars = ax.bar(categories, ys, color=["#6C8EBF", "#8E7DBE", "#57A773", "#E07A00"])
        for b, y in zip(bars, ys):
            if np.isfinite(y):
                ax.text(b.get_x() + b.get_width() / 2, y, f"{y:.3f}", ha="center", va="bottom", fontsize=8)
        ax.set_ylabel("Score")
    else:
        ys = [0.66, 0.62, 0.64, 0.72]
        bars = ax.bar(categories, ys, color=["#B7C4D8", "#C8BBD9", "#BBD9C4", "#F2D0A7"])
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.01, "TBD", ha="center", va="bottom", fontsize=8)
        ax.set_ylim(0.0, 0.85)
        ax.text(0.02, 0.95, "Placeholder: replace with reproducible run outputs", transform=ax.transAxes, fontsize=8, color="#59667A")
        ax.set_ylabel("Accuracy (placeholder)")
    ax.set_title("Ablation Comparison")
    _save_plot(fig, outpath)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate evaluation SVG plots from simulation CSV outputs.")
    parser.add_argument(
        "--input-dir",
        action="append",
        default=["."],
        help="Directory to recursively scan for CSV files (repeatable).",
    )
    parser.add_argument(
        "--csv",
        action="append",
        default=[],
        help="Explicit CSV file path (repeatable).",
    )
    parser.add_argument(
        "--out-dir",
        default="figures/eval",
        help="Output directory for generated SVG files.",
    )
    args = parser.parse_args()

    input_dirs = [Path(d).resolve() for d in args.input_dir]
    explicit_csvs = [Path(p).resolve() for p in args.csv]
    out_dir = Path(args.out_dir).resolve()

    csv_paths = _collect_csvs(input_dirs, explicit_csvs)
    _setup_style()

    reward_series: List[Series] = []
    acc_series: List[Series] = []
    gap_series: List[Series] = []
    alpha_values: List[np.ndarray] = []
    selected_policies = [
        "learned_mixed",
        "vector_topk",
        "vector_topk_rerank",
        "pointer_chase",
        "graph_prior_only",
        "random",
        "oracle",
    ]
    policy_norm_map = {_norm(p): p for p in selected_policies}

    for csv_path in csv_paths:
        headers, rows = _read_csv(csv_path)
        if not headers or not rows:
            continue
        policy_col = _first_matching(headers, ("policy", "mode", "router", "setting", "arm"))
        if policy_col:
            grouped: Dict[str, List[Dict[str, str]]] = {p: [] for p in selected_policies}
            for row in rows:
                raw_policy = (row.get(policy_col) or "").strip()
                norm_policy = _norm(raw_policy)
                canonical = policy_norm_map.get(norm_policy)
                if canonical:
                    grouped[canonical].append(row)

            for policy in selected_policies:
                policy_rows = grouped.get(policy) or []
                if not policy_rows:
                    continue
                label = policy.replace("_", " ")
                reward = _extract_series_from_rows(
                    headers,
                    policy_rows,
                    ("reward", "mean_reward", "avg_reward", "return", "episode_reward"),
                    default_label=label,
                )
                if reward:
                    reward_series.append(reward)

                acc = _extract_series_from_rows(
                    headers,
                    policy_rows,
                    ("accuracy", "acc", "success_rate", "task_success", "correctness"),
                    default_label=label,
                )
                if acc:
                    acc_series.append(acc)

                gap = _extract_gap_closed_from_rows(headers, policy_rows, default_label=label)
                if gap:
                    gap_series.append(gap)
        else:
            reward = _extract_series(csv_path, ("reward", "mean_reward", "avg_reward", "return", "episode_reward"))
            if reward:
                reward.label = _pick_label(csv_path)
                reward_series.append(reward)

            acc = _extract_series(csv_path, ("accuracy", "acc", "success_rate", "task_success", "correctness"))
            if acc:
                acc.label = _pick_label(csv_path)
                acc_series.append(acc)

            gap = _extract_gap_closed(csv_path)
            if gap:
                gap.label = _pick_label(csv_path)
                gap_series.append(gap)

        alpha = _extract_alpha_values(csv_path)
        if alpha is not None:
            alpha_values.append(alpha)

    _plot_line(
        reward_series,
        out_dir / "reward_vs_epoch.svg",
        "Reward vs Epoch",
        "Reward",
    )
    _plot_line(
        acc_series,
        out_dir / "accuracy_vs_epoch.svg",
        "Accuracy vs Epoch",
        "Accuracy",
        y_lim=(0.0, 1.0),
    )
    _plot_line(
        gap_series,
        out_dir / "oracle_gap_closed.svg",
        "Oracle Gap Closed vs Epoch",
        "Gap Closed",
        y_lim=(0.0, 1.0),
    )

    alpha_merged = np.concatenate(alpha_values) if alpha_values else None
    _plot_hist(alpha_merged, out_dir / "alpha_router_conf_hist.svg", "Router Confidence Mix (alpha) Histogram")

    _build_ablation_chart(csv_paths, out_dir / "ablation_bar_chart.svg")

    print(f"Generated figures in: {out_dir}")
    print("- reward_vs_epoch.svg")
    print("- accuracy_vs_epoch.svg")
    print("- oracle_gap_closed.svg")
    print("- alpha_router_conf_hist.svg")
    print("- ablation_bar_chart.svg")


if __name__ == "__main__":
    main()
