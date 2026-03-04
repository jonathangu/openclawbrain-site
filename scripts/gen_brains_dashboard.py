#!/usr/bin/env python3
"""Generate brain dashboard charts.

Requires: matplotlib
If matplotlib is missing, the script will exit with a helpful message.
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except ImportError:  # pragma: no cover - runtime guard
    print("ERROR: matplotlib is required. Install with: pip install matplotlib", file=sys.stderr)
    sys.exit(1)


def _set_dark_theme() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "#0b0f14",
            "axes.facecolor": "#0f172a",
            "axes.edgecolor": "#334155",
            "axes.labelcolor": "#e2e8f0",
            "xtick.color": "#cbd5f5",
            "ytick.color": "#cbd5f5",
            "text.color": "#e2e8f0",
            "grid.color": "#334155",
            "grid.alpha": 0.35,
            "axes.titleweight": "bold",
            "font.size": 11,
        }
    )


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _save(fig, path: Path) -> None:
    fig.savefig(path, dpi=160, bbox_inches="tight", facecolor=fig.get_facecolor())
    plt.close(fig)


def main() -> int:
    data = [
        {
            "agent": "main",
            "nodes": 12944,
            "edges": 75213,
            "reflex": 30.6,
            "habitual": 27.1,
            "dormant": 42.4,
            "inhibitory": 87,
        },
        {
            "agent": "pelican",
            "nodes": 10532,
            "edges": 51958,
            "reflex": 18.4,
            "habitual": 42.4,
            "dormant": 39.2,
            "inhibitory": 42,
        },
        {
            "agent": "bountiful",
            "nodes": 1928,
            "edges": 30001,
            "reflex": 5.0,
            "habitual": 27.5,
            "dormant": 67.5,
            "inhibitory": 79,
        },
        {
            "agent": "family",
            "nodes": 131,
            "edges": 1701,
            "reflex": 2.5,
            "habitual": 49.4,
            "dormant": 48.0,
            "inhibitory": 69,
        },
    ]

    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / "assets" / "brains-dashboard"
    _ensure_dir(out_dir)

    agents = [d["agent"] for d in data]
    nodes = [d["nodes"] for d in data]
    edges = [d["edges"] for d in data]
    inhibitory = [d["inhibitory"] for d in data]

    tiers = []
    for d in data:
        total = d["reflex"] + d["habitual"] + d["dormant"]
        if total <= 0:
            tiers.append((0.0, 0.0, 0.0))
        else:
            scale = 100.0 / total
            tiers.append((d["reflex"] * scale, d["habitual"] * scale, d["dormant"] * scale))

    reflex = [t[0] for t in tiers]
    habitual = [t[1] for t in tiers]
    dormant = [t[2] for t in tiers]

    _set_dark_theme()

    # Nodes + edges (two subplots)
    fig, axes = plt.subplots(2, 1, figsize=(8.5, 6.5), sharex=True)
    fig.suptitle("Brain Graph Size by Agent", fontsize=14, y=0.98)

    axes[0].bar(agents, nodes, color="#38bdf8")
    axes[0].set_ylabel("Nodes")
    axes[0].grid(axis="y", linestyle="--", linewidth=0.6)

    axes[1].bar(agents, edges, color="#f472b6")
    axes[1].set_ylabel("Edges")
    axes[1].grid(axis="y", linestyle="--", linewidth=0.6)

    _save(fig, out_dir / "brains_dashboard_nodes_edges.png")

    # Tiers (stacked bar)
    fig, ax = plt.subplots(figsize=(8.5, 5.5))
    fig.suptitle("Brain Tiers by Agent", fontsize=14, y=0.98)

    ax.bar(agents, reflex, label="Reflex", color="#22c55e")
    ax.bar(agents, habitual, bottom=reflex, label="Habitual", color="#f59e0b")
    bottom = [r + h for r, h in zip(reflex, habitual)]
    ax.bar(agents, dormant, bottom=bottom, label="Dormant", color="#a78bfa")

    ax.set_ylabel("Share of edges (%)")
    ax.set_ylim(0, 100)
    ax.grid(axis="y", linestyle="--", linewidth=0.6)
    ax.legend(frameon=False, ncols=3, loc="upper center", bbox_to_anchor=(0.5, 1.05))

    _save(fig, out_dir / "brains_dashboard_tiers.png")

    # Inhibitory edges
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    fig.suptitle("Inhibitory Edges by Agent", fontsize=14, y=0.98)

    ax.bar(agents, inhibitory, color="#f97316")
    ax.set_ylabel("Inhibitory edges")
    ax.grid(axis="y", linestyle="--", linewidth=0.6)

    _save(fig, out_dir / "brains_dashboard_inhibitory.png")

    print(f"Charts written to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
