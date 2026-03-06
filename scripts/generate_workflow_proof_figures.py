#!/usr/bin/env python3
"""Generate lightweight SVG figures from workflow-proof CSV artifacts."""

from __future__ import annotations

import argparse
import csv
from html import escape
from pathlib import Path
from typing import Dict, Iterable, List, Sequence


MODE_ORDER = ["vector_topk", "pointer_chase", "graph_prior_only", "learned"]
MODE_LABELS = {
    "vector_topk": "vector_topk",
    "pointer_chase": "pointer_chase",
    "graph_prior_only": "graph_prior_only",
    "learned": "learned",
}
MODE_COLORS = {
    "vector_topk": "#5f7486",
    "pointer_chase": "#ffbe72",
    "graph_prior_only": "#9ce0bc",
    "learned": "#79d3ff",
}
BG = "#09141d"
PANEL = "#0d1b27"
GRID = "#1f3445"
TEXT = "#dce8f1"
MUTED = "#97afbf"
ACCENT = "#79d3ff"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline",
        default="/private/tmp/ocb-proof-sims/scratch/workflow-proof/latest/baseline_eval/summary.csv",
        help="Path to baseline_eval/summary.csv",
    )
    parser.add_argument(
        "--curve",
        default="/private/tmp/ocb-proof-sims/scratch/workflow-proof/latest/learning_curve.csv",
        help="Path to learning_curve.csv",
    )
    parser.add_argument(
        "--outdir",
        default="figures/eval",
        help="Directory to write the generated SVG figures into",
    )
    return parser.parse_args()


def read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def parse_float(row: Dict[str, str], key: str) -> float:
    value = row.get(key)
    if value is None or value == "":
        raise ValueError(f"missing {key!r} in row: {row}")
    return float(value)


def load_baseline(path: Path) -> Dict[str, Dict[str, float]]:
    rows = read_csv(path)
    buckets: Dict[str, Dict[str, List[float]]] = {
        mode: {"target_success": [], "required_node_coverage": []} for mode in MODE_ORDER
    }
    for row in rows:
        mode = row.get("mode", "")
        if mode not in buckets:
            continue
        buckets[mode]["target_success"].append(parse_float(row, "target_success"))
        buckets[mode]["required_node_coverage"].append(parse_float(row, "required_node_coverage"))

    missing = [mode for mode in MODE_ORDER if not buckets[mode]["target_success"]]
    if missing:
        raise ValueError(f"baseline CSV missing modes: {', '.join(missing)}")
    return {
        mode: {
            key: sum(values) / len(values)
            for key, values in metrics.items()
        }
        for mode, metrics in buckets.items()
    }


def load_curve(path: Path) -> List[Dict[str, float]]:
    rows = read_csv(path)
    points: List[Dict[str, float]] = []
    for row in rows:
        points.append(
            {
                "epoch": parse_float(row, "epoch"),
                "graph": parse_float(row, "graph_prior_target_success_rate"),
                "learned": parse_float(row, "learned_target_success_rate"),
            }
        )
    if not points:
        raise ValueError("learning curve CSV is empty")
    return points


def svg_text(
    x: float,
    y: float,
    text: str,
    *,
    fill: str = TEXT,
    size: int = 16,
    weight: int = 400,
    family: str = "'Space Grotesk', 'Arial', sans-serif",
    anchor: str = "start",
    letter_spacing: float | None = None,
) -> str:
    attrs = [
        f'x="{x:.1f}"',
        f'y="{y:.1f}"',
        f'fill="{fill}"',
        f'font-size="{size}"',
        f'font-weight="{weight}"',
        f'font-family="{family}"',
        f'text-anchor="{anchor}"',
    ]
    if letter_spacing is not None:
        attrs.append(f'letter-spacing="{letter_spacing}"')
    return f"<text {' '.join(attrs)}>{escape(text)}</text>"


def svg_rect(
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    fill: str,
    stroke: str | None = None,
    stroke_width: float = 1,
    radius: float = 0,
    opacity: float | None = None,
) -> str:
    attrs = [
        f'x="{x:.1f}"',
        f'y="{y:.1f}"',
        f'width="{width:.1f}"',
        f'height="{height:.1f}"',
        f'fill="{fill}"',
    ]
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{stroke_width}"')
    if radius:
        attrs.append(f'rx="{radius:.1f}"')
        attrs.append(f'ry="{radius:.1f}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f"<rect {' '.join(attrs)} />"


def svg_line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    *,
    stroke: str,
    stroke_width: float = 1,
    dasharray: str | None = None,
    opacity: float | None = None,
) -> str:
    attrs = [
        f'x1="{x1:.1f}"',
        f'y1="{y1:.1f}"',
        f'x2="{x2:.1f}"',
        f'y2="{y2:.1f}"',
        f'stroke="{stroke}"',
        f'stroke-width="{stroke_width}"',
        'stroke-linecap="round"',
    ]
    if dasharray:
        attrs.append(f'stroke-dasharray="{dasharray}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f"<line {' '.join(attrs)} />"


def svg_circle(cx: float, cy: float, r: float, *, fill: str, stroke: str | None = None, stroke_width: float = 1) -> str:
    attrs = [f'cx="{cx:.1f}"', f'cy="{cy:.1f}"', f'r="{r:.1f}"', f'fill="{fill}"']
    if stroke:
        attrs.append(f'stroke="{stroke}"')
        attrs.append(f'stroke-width="{stroke_width}"')
    return f"<circle {' '.join(attrs)} />"


def svg_polyline(points: Sequence[tuple[float, float]], *, stroke: str, stroke_width: float = 3, fill: str = "none", dasharray: str | None = None, opacity: float | None = None) -> str:
    attrs = [
        'points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in points) + '"',
        f'stroke="{stroke}"',
        f'stroke-width="{stroke_width}"',
        f'fill="{fill}"',
        'stroke-linecap="round"',
        'stroke-linejoin="round"',
    ]
    if dasharray:
        attrs.append(f'stroke-dasharray="{dasharray}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f"<polyline {' '.join(attrs)} />"


def svg_polygon(points: Sequence[tuple[float, float]], *, fill: str, opacity: float) -> str:
    attr = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{attr}" fill="{fill}" opacity="{opacity}" />'


def chart_frame(width: int, height: int, title: str, desc: str) -> List[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f"<title>{escape(title)}</title>",
        f"<desc>{escape(desc)}</desc>",
        svg_rect(0, 0, width, height, fill=BG),
        svg_rect(24, 24, width - 48, height - 48, fill=PANEL, stroke="#173042", stroke_width=1, radius=28),
    ]


def write_svg(path: Path, lines: Iterable[str]) -> None:
    path.write_text("\n".join([*lines, "</svg>", ""]), encoding="utf-8")


def render_baseline_chart(values: Dict[str, Dict[str, float]], out_path: Path) -> None:
    width, height = 1160, 720
    left, right = 110, width - 86
    top, bottom = 190, height - 170
    plot_width = right - left
    plot_height = bottom - top
    lines = chart_frame(
        width,
        height,
        "Exact-target success on the deterministic workflow-proof harness",
        "Bar chart comparing vector_topk, pointer_chase, graph_prior_only, and learned exact-target success across four fixed queries.",
    )
    lines.extend(
        [
            svg_text(78, 92, "Deterministic workflow proof", fill=ACCENT, size=18, weight=700, letter_spacing=1.4),
            svg_text(78, 130, "Exact-target success on the same 4 fixed workflow queries", size=34, weight=700),
            svg_text(78, 162, "Metric: both required nodes retrieved into the bounded prompt context.", fill=MUTED, size=18),
        ]
    )

    for tick in range(0, 101, 25):
        y = bottom - (tick / 100.0) * plot_height
        lines.append(svg_line(left, y, right, y, stroke=GRID, stroke_width=1))
        lines.append(svg_text(left - 16, y + 6, f"{tick}%", fill=MUTED, size=15, anchor="end", family="'IBM Plex Mono', monospace"))

    lines.append(svg_line(left, bottom, right, bottom, stroke="#284357", stroke_width=2))

    slot_width = plot_width / len(MODE_ORDER)
    bar_width = 128
    for idx, mode in enumerate(MODE_ORDER):
        value = values[mode]["target_success"]
        bar_height = plot_height * value
        x = left + slot_width * idx + (slot_width - bar_width) / 2
        y = bottom - bar_height
        if value > 0:
            lines.append(svg_rect(x, y, bar_width, bar_height, fill=MODE_COLORS[mode], radius=20))
            label_y = y - 14
        else:
            lines.append(svg_line(x, bottom, x + bar_width, bottom, stroke=MODE_COLORS[mode], stroke_width=4))
            label_y = bottom - 16
        lines.extend(
            [
                svg_text(x + bar_width / 2, label_y, f"{int(round(value * 4))}/4", fill=TEXT, size=24, weight=700, anchor="middle"),
                svg_text(x + bar_width / 2, bottom + 36, MODE_LABELS[mode], fill=TEXT, size=16, weight=600, anchor="middle", family="'IBM Plex Mono', monospace"),
                svg_text(x + bar_width / 2, bottom + 62, f"{int(round(value * 100))}% exact-target success", fill=MUTED, size=15, anchor="middle"),
            ]
        )

    lines.extend(
        [
            svg_rect(76, 584, width - 152, 82, fill="#0a1823", stroke="#173042", stroke_width=1, radius=20),
            svg_text(
                102,
                617,
                "Required-node coverage mean: "
                + ", ".join(
                    f"{mode} {values[mode]['required_node_coverage']:.2f}" for mode in MODE_ORDER
                )
                + ".",
                fill=TEXT,
                size=17,
                weight=500,
            ),
            svg_text(102, 647, "Current deterministic result only. This makes the retrieval improvement concrete; it does not prove live OpenClaw task success.", fill=MUTED, size=16),
        ]
    )
    write_svg(out_path, lines)


def render_learning_curve(points: List[Dict[str, float]], out_path: Path) -> None:
    width, height = 1160, 720
    left, right = 110, width - 86
    top, bottom = 190, height - 150
    plot_width = right - left
    plot_height = bottom - top
    first_epoch = points[0]["epoch"]
    last_epoch = points[-1]["epoch"]

    def x_for(epoch: float) -> float:
        span = max(last_epoch - first_epoch, 1.0)
        return left + ((epoch - first_epoch) / span) * plot_width

    def y_for(value: float) -> float:
        return bottom - value * plot_height

    graph_points = [(x_for(point["epoch"]), y_for(point["graph"])) for point in points]
    learned_points = [(x_for(point["epoch"]), y_for(point["learned"])) for point in points]
    first_full = next(point["epoch"] for point in points if point["learned"] >= 1.0)
    marker_x = x_for(first_full)
    lines = chart_frame(
        width,
        height,
        "Learning curve for graph prior versus learned routing",
        "Line chart showing graph prior exact-target success flat at fifty percent while learned routing reaches one hundred percent by epoch fourteen.",
    )
    lines.extend(
        [
            svg_text(78, 92, "Deterministic workflow proof", fill=ACCENT, size=18, weight=700, letter_spacing=1.4),
            svg_text(78, 130, "Graph prior stays flat while learned routing reaches full success by epoch 14", size=34, weight=700),
            svg_text(78, 162, "Same 4 fixed workflow queries across 16 teacher-supervised epochs.", fill=MUTED, size=18),
        ]
    )

    for tick in range(0, 101, 25):
        y = y_for(tick / 100.0)
        lines.append(svg_line(left, y, right, y, stroke=GRID, stroke_width=1))
        lines.append(svg_text(left - 16, y + 6, f"{tick}%", fill=MUTED, size=15, anchor="end", family="'IBM Plex Mono', monospace"))

    tick_epochs = [1, 4, 8, 12, 14, 16]
    for epoch in tick_epochs:
        x = x_for(float(epoch))
        lines.append(svg_line(x, top, x, bottom, stroke=GRID, stroke_width=1, opacity=0.55))
        lines.append(svg_text(x, bottom + 32, f"{epoch}", fill=MUTED, size=15, anchor="middle", family="'IBM Plex Mono', monospace"))
    lines.append(svg_text((left + right) / 2, bottom + 62, "Epoch", fill=MUTED, size=16, anchor="middle"))

    learned_fill = [(left, bottom), *learned_points, (right, bottom)]
    lines.append(svg_polygon(learned_fill, fill=ACCENT, opacity=0.10))
    lines.append(svg_polyline(graph_points, stroke=MODE_COLORS["graph_prior_only"], stroke_width=4, dasharray="12 10"))
    lines.append(svg_polyline(learned_points, stroke=MODE_COLORS["learned"], stroke_width=5))
    for x, y in graph_points:
        lines.append(svg_circle(x, y, 4.5, fill=MODE_COLORS["graph_prior_only"], stroke=PANEL, stroke_width=2))
    for x, y in learned_points:
        lines.append(svg_circle(x, y, 4.5, fill=MODE_COLORS["learned"], stroke=PANEL, stroke_width=2))

    lines.append(svg_line(marker_x, top, marker_x, bottom, stroke="#ff8e66", stroke_width=2.5, dasharray="8 8"))
    lines.append(svg_rect(marker_x - 114, top + 12, 228, 44, fill="#112433", stroke="#ff8e66", stroke_width=1, radius=14))
    lines.append(svg_text(marker_x, top + 40, "epoch 14: learned reaches 4/4", fill=TEXT, size=17, weight=600, anchor="middle"))

    lines.append(svg_rect(744, 238, 290, 116, fill="#0a1823", stroke="#173042", stroke_width=1, radius=18))
    lines.append(svg_circle(772, 268, 7, fill=MODE_COLORS["graph_prior_only"]))
    lines.append(svg_text(790, 274, "graph_prior_only", fill=TEXT, size=17, weight=600, family="'IBM Plex Mono', monospace"))
    lines.append(svg_text(790, 300, "2/4 exact-target success from epoch 1 through 16", fill=MUTED, size=15))
    lines.append(svg_circle(772, 330, 7, fill=MODE_COLORS["learned"]))
    lines.append(svg_text(790, 336, "learned", fill=TEXT, size=17, weight=600, family="'IBM Plex Mono', monospace"))
    lines.append(svg_text(790, 362, "2/4 until epoch 13, then 4/4 from epoch 14 onward", fill=MUTED, size=15))

    lines.extend(
        [
            svg_rect(76, 590, width - 152, 74, fill="#0a1823", stroke="#173042", stroke_width=1, radius=20),
            svg_text(102, 622, "This is a controlled mechanism result: graph priors help immediately, then the learned runtime route_fn improves later off the hot path.", fill=TEXT, size=17, weight=500),
            svg_text(102, 649, "It still needs recorded-session, shadow, and online evidence before any production win claim.", fill=MUTED, size=16),
        ]
    )
    write_svg(out_path, lines)


def main() -> None:
    args = parse_args()
    baseline_path = Path(args.baseline)
    curve_path = Path(args.curve)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    baseline_values = load_baseline(baseline_path)
    curve_points = load_curve(curve_path)

    render_baseline_chart(baseline_values, outdir / "workflow_proof_exact_target_success.svg")
    render_learning_curve(curve_points, outdir / "workflow_proof_learning_curve.svg")


if __name__ == "__main__":
    main()
