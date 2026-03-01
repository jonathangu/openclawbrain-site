#!/usr/bin/env python3
"""Generate publication-quality figures for the OpenClawBrain v12 paper."""

from pathlib import Path
import json

import matplotlib.pyplot as plt
import numpy as np

COLOR_PG = "#2563eb"
COLOR_HEURISTIC = "#ea580c"
COLOR_GREEN = "#16a34a"
COLOR_GRAY = "#6b7280"
COLOR_DORMANT = "#fecaca"
COLOR_HABITUAL = "#86efac"
COLOR_REFLEX = "#bfdbfe"

LANDSCAPE_SIZE = (8, 4.5)
FREQUENCY_SIZE = (8, 4.0)
PRODUCTION_SIZE = (8, 3.5)
DPI = 250
LINE_WIDTH = 2.0
DRIFT_LINE_WIDTH = 1.5

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.size"] = 12


def moving_average(values, window=15):
    values = np.asarray(values, dtype=float)
    if window <= 1:
        return values
    cumsum = np.cumsum(values)
    smoothed = np.empty_like(values)
    for idx in range(len(values)):
        start = max(0, idx - window + 1)
        window_sum = cumsum[idx] - (cumsum[start - 1] if start > 0 else 0.0)
        smoothed[idx] = window_sum / (idx - start + 1)
    return smoothed


def add_concept_drift(ax):
    ax.axvline(200, color=COLOR_GRAY, linestyle="--", linewidth=DRIFT_LINE_WIDTH)
    ax.text(200, 0.05, "Concept drift", color=COLOR_GRAY, fontsize=11, ha="left", va="bottom")


def style_axes(ax, *, x_step_ticks=False):
    ax.patch.set_facecolor("white")
    ax.set_facecolor("white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color="#e0e0e0", linewidth=0.6, alpha=0.7)
    ax.tick_params(labelsize=11)
    if x_step_ticks:
        max_step = int(ax.get_xlim()[1])
        ax.set_xticks(np.arange(0, max_step + 1, 50))


def save(fig, path):
    fig.patch.set_facecolor("white")
    fig.tight_layout()
    fig.savefig(path, dpi=DPI, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)


def plot_gate_evolution(run):
    ts = run["pg"]["timeseries"]
    steps = np.arange(len(ts["gate_A"]))

    fig, ax = plt.subplots(figsize=LANDSCAPE_SIZE)
    ax.plot(steps, ts["gate_A"], label="Gate A", color=COLOR_PG, linewidth=LINE_WIDTH)
    ax.plot(steps, ts["gate_B"], label="Gate B", color=COLOR_GREEN, linewidth=LINE_WIDTH)
    ax.plot(steps, ts["gate_C"], label="Gate C", color=COLOR_HEURISTIC, linewidth=LINE_WIDTH)

    ax.set_title("Gate weight evolution under policy-gradient learning")
    ax.set_xlabel("Step")
    ax.set_ylabel("Edge weight")
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.legend(loc="lower right", frameon=False, fontsize=11)
    style_axes(ax, x_step_ticks=True)
    add_concept_drift(ax)
    save(fig, Path("figures") / "pg_gate_evolution.png")


def plot_separation(run):
    ts_pg = run["pg"]["timeseries"]
    ts_h = run["heuristic"]["timeseries"]
    steps = np.arange(len(ts_pg["separation"]))

    fig, ax = plt.subplots(figsize=LANDSCAPE_SIZE)
    ax.plot(
        steps,
        moving_average(ts_pg["separation"], window=15),
        label="Policy gradient",
        color=COLOR_PG,
        linewidth=LINE_WIDTH,
    )
    ax.plot(
        steps,
        moving_average(ts_h["separation"], window=15),
        label="Heuristic",
        color=COLOR_HEURISTIC,
        linewidth=LINE_WIDTH,
    )

    ax.set_title("Branch separation: policy gradient vs heuristic (15-step rolling mean)")
    ax.set_xlabel("Step")
    ax.set_ylabel("Branch separation")
    ax.legend(loc="upper right", frameon=False, fontsize=11)
    style_axes(ax, x_step_ticks=True)
    add_concept_drift(ax)
    save(fig, Path("figures") / "pg_vs_heuristic_separation.png")


def plot_total_weight(run):
    ts_pg = run["pg"]["timeseries"]
    ts_h = run["heuristic"]["timeseries"]
    steps = np.arange(len(ts_pg["total_weight"]))

    fig, ax = plt.subplots(figsize=LANDSCAPE_SIZE)
    ax.plot(
        steps,
        ts_pg["total_weight"],
        label="Policy gradient",
        color=COLOR_PG,
        linewidth=LINE_WIDTH,
    )
    ax.plot(
        steps,
        ts_h["total_weight"],
        label="Heuristic",
        color=COLOR_HEURISTIC,
        linewidth=LINE_WIDTH,
    )

    ax.set_title("Total graph weight: PG bounded vs heuristic inflation")
    ax.set_xlabel("Step")
    ax.set_ylabel("Total graph weight")
    ax.legend(loc="upper right", frameon=False, fontsize=11)
    style_axes(ax, x_step_ticks=True)
    add_concept_drift(ax)
    save(fig, Path("figures") / "pg_vs_heuristic_weight.png")


def plot_equilibrium_by_frequency():
    labels = ["0x/day", "1x/day", "2x/day", "3x/day", "5x/day", "10x/day"]
    values = np.array([0.0, 0.236, 0.473, 0.710, 0.966, 0.980], dtype=float)
    x = np.arange(len(labels))

    colors = []
    for value in values:
        if value < 0.15:
            colors.append("#dc2626")  # red for pruned/dead
        elif value < 0.6:
            colors.append(COLOR_GREEN)  # green for habitual
        else:
            colors.append(COLOR_PG)  # blue for reflex

    fig, ax = plt.subplots(figsize=FREQUENCY_SIZE)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")

    # Subtle tier boundary lines instead of colored bands
    ax.axhline(0.15, color="#999999", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.axhline(0.6, color="#999999", linestyle="--", linewidth=0.8, alpha=0.6)
    ax.text(x[-1] + 0.35, 0.075, "Dormant", ha="left", va="center", fontsize=10, color="#888")
    ax.text(x[-1] + 0.35, 0.375, "Habitual", ha="left", va="center", fontsize=10, color="#888")
    ax.text(x[-1] + 0.35, 0.8, "Reflex", ha="left", va="center", fontsize=10, color="#888")

    ax.bar(x, values, color=colors, width=0.6)
    ax.set_title("Steady-state weight by reinforcement frequency")
    ax.set_xlabel("Reinforcement frequency")
    ax.set_ylabel("Equilibrium weight")
    ax.set_xticks(x, labels)
    ax.set_ylim(0, 1.05)
    ax.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlim(-0.6, x[-1] + 1.2)
    ax.legend([], frameon=False)
    style_axes(ax)
    save(fig, Path("figures") / "equilibrium_by_frequency.png")


def _annotate_hbars(ax, values, y_positions, height):
    for value, y in zip(values, y_positions):
        ax.text(
            value + (max(values) * 0.01),
            y,
            f"{int(value):,}",
            va="center",
            ha="left",
            fontsize=10,
        )


def plot_production_brains():
    brains = ["GUCLAW (1,160 nodes)", "Pelican (584 nodes)", "Bountiful (286 nodes)"]
    nodes = np.array([1160, 584, 286], dtype=float)
    edges = np.array([2554, 2100, 943], dtype=float)
    positions = np.arange(len(brains))
    bar_height = 0.35
    x_max = max(np.max(nodes), np.max(edges))

    fig, ax = plt.subplots(figsize=PRODUCTION_SIZE)
    ax.set_xlim(0, x_max * 1.15)
    ax.barh(
        positions - bar_height / 2,
        nodes,
        height=bar_height,
        label="Nodes",
        color=COLOR_PG,
    )
    ax.barh(
        positions + bar_height / 2,
        edges,
        height=bar_height,
        label="Edges",
        color=COLOR_GREEN,
    )
    _annotate_hbars(ax, nodes, positions - bar_height / 2, bar_height)
    _annotate_hbars(ax, edges, positions + bar_height / 2, bar_height)

    ax.set_title("Production brains running OpenClawBrain v12.2.0")
    ax.set_xlabel("Count")
    ax.set_yticks(positions)
    ax.set_yticklabels(brains)
    ax.legend(frameon=False, fontsize=11)
    style_axes(ax)
    save(fig, Path("figures") / "production_brains.png")


def main():
    results_path = Path.home() / "openclawbrain/sims/pg_vs_heuristic_v2_results.json"
    with results_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)

    run = payload["runs"][0]
    Path("figures").mkdir(exist_ok=True)
    plot_gate_evolution(run)
    plot_separation(run)
    plot_total_weight(run)
    plot_equilibrium_by_frequency()
    plot_production_brains()


if __name__ == "__main__":
    main()
