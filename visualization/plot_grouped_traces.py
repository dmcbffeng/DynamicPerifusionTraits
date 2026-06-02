"""
Grouped perifusion trace visualization (one mean + 95% CI line per group).
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from plot_traces import STIMULUS_SEGMENTS, _infer_label_from_filename, _prepare_trace_data

plt.rcParams["font.family"] = "Arial"


def _read_group_assignments(group_csv: Path) -> pd.DataFrame:
    group_df = pd.read_csv(group_csv)
    normalized = {str(col).strip().lower(): col for col in group_df.columns}

    donor_key = None
    group_key = None
    for key, raw in normalized.items():
        if donor_key is None and ("donor" in key or "rrid" in key or "sample" in key):
            donor_key = raw
        if group_key is None and "group" in key:
            group_key = raw

    if donor_key is None or group_key is None:
        raise ValueError(
            "Group assignment CSV must include donor/sample id and group columns "
            "(e.g., donor_id, group)."
        )

    parsed = group_df[[donor_key, group_key]].copy()
    parsed.columns = ["donor_id", "group"]
    parsed["donor_id"] = parsed["donor_id"].astype(str).str.strip()
    parsed["group"] = parsed["group"].astype(str).str.strip()
    parsed = parsed[parsed["donor_id"] != ""]
    parsed = parsed[parsed["group"] != ""]
    return parsed


def _plot_top_annotations(ax: plt.Axes, y_top: float) -> None:
    boundary_h = y_top * 0.004
    bar_y = y_top + boundary_h
    bar_h = y_top * 0.025
    text_y = bar_y + bar_h + y_top * 0.004

    ax.add_patch(
        plt.Rectangle(
            (0, y_top),
            150,
            boundary_h,
            facecolor="black",
            edgecolor="none",
            clip_on=False,
            zorder=7,
        )
    )

    for start, end, label in STIMULUS_SEGMENTS:
        is_stimulus = label != "G 5.6"
        if is_stimulus:
            ax.add_patch(
                plt.Rectangle(
                    (start, bar_y),
                    end - start,
                    bar_h,
                    facecolor="#505050",
                    edgecolor="none",
                    clip_on=False,
                    zorder=8,
                )
            )
            ax.text(
                (start + end) / 2,
                text_y,
                label,
                ha="center",
                va="bottom",
                fontsize=16,
                weight="bold",
                clip_on=False,
                zorder=9,
            )
        else:
            ax.text(
                (start + end) / 2,
                y_top * 0.985,
                label,
                ha="center",
                va="top",
                fontsize=14,
                weight="bold",
                clip_on=True,
                zorder=9,
            )


def visualize_grouped_trace_csv(
    csv_path: str | Path,
    group_csv_path: str | Path,
    output_path: str | Path | None = None,
    dpi: int = 300,
    y_upper: float | None = None,
    y_scale: float = 1.2,
) -> Path:
    """
    Plot one mean trace with 95% CI for each user-defined group.
    """
    csv_path = Path(csv_path)
    group_csv_path = Path(group_csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")
    if not group_csv_path.exists():
        raise FileNotFoundError(f"Group CSV not found: {group_csv_path}")

    raw_df = pd.read_csv(csv_path)
    time_x, trace_df = _prepare_trace_data(raw_df)
    y_label = _infer_label_from_filename(csv_path)

    assignments = _read_group_assignments(group_csv_path)
    donor_to_group: Dict[str, str] = dict(
        zip(assignments["donor_id"].tolist(), assignments["group"].tolist())
    )

    grouped_columns: Dict[str, List[str]] = {}
    for donor_col in trace_df.columns:
        if donor_col in donor_to_group:
            grp = donor_to_group[donor_col]
            grouped_columns.setdefault(grp, []).append(donor_col)

    if not grouped_columns:
        raise ValueError(
            "No overlap found between donor IDs in trace CSV and group assignment CSV."
        )

    if output_path is None:
        output_path = csv_path.with_name(f"{csv_path.stem}_grouped_trace.png")
    output_path = Path(output_path)

    y_max = np.nanmax(trace_df.to_numpy(dtype=float))
    if not np.isfinite(y_max) or y_max <= 0:
        y_max = 1.0
    y_upper_candidate = y_max

    fig, ax = plt.subplots(figsize=(11.5, 6))

    # Yellow windows indicate stimulus phases (non-G 5.6).
    for start, end, label in STIMULUS_SEGMENTS:
        if label != "G 5.6":
            ax.axvspan(start, end, color="#f7f5cf", alpha=0.7, zorder=0)

    boundaries = sorted({segment[0] for segment in STIMULUS_SEGMENTS[1:]})
    for x in boundaries:
        ax.axvline(x=x, color="#d8d8d8", linestyle=":", linewidth=1.0, zorder=1)

    palette = plt.cm.tab10(np.linspace(0, 1, max(3, len(grouped_columns))))
    sorted_groups = sorted(grouped_columns.items())
    for idx, (group_name, donors) in enumerate(sorted_groups):
        group_df = trace_df[donors]
        mean = group_df.mean(axis=1, skipna=True)
        sem = group_df.sem(axis=1, skipna=True)
        ci_half_width = 1.96 * sem.fillna(0.0)
        ci_lower = mean - ci_half_width
        ci_upper_series = mean + ci_half_width
        color = palette[idx]
        display_label = str(group_name).strip()
        upper_for_group = float(np.nanmax(ci_upper_series.to_numpy(dtype=float)))
        if np.isfinite(upper_for_group):
            y_upper_candidate = max(y_upper_candidate, upper_for_group)

        ax.fill_between(
            time_x.to_numpy(),
            ci_lower.to_numpy(),
            ci_upper_series.to_numpy(),
            color=color,
            alpha=0.35,
            linewidth=0,
            zorder=2,
        )
        ax.plot(
            time_x,
            mean,
            color=color,
            linewidth=2.2,
            marker="o",
            markersize=3.2,
            markeredgewidth=0.0,
            zorder=3,
            label=f"{display_label} (n={len(donors)})",
        )

    ax.set_xlim(0, 150)
    if y_upper is not None:
        if y_upper <= 0:
            raise ValueError("y_upper must be positive when provided.")
        y_axis_top = y_upper
    else:
        if y_scale <= 0:
            raise ValueError("y_scale must be positive.")
        y_axis_top = y_upper_candidate * y_scale
    ax.set_ylim(0, y_axis_top)
    ax.set_xticks([0, 30, 60, 90, 120, 150])
    ax.set_xlabel("Time (min)", fontsize=16)
    ax.set_ylabel(y_label, fontsize=20)
    ax.tick_params(axis="both", labelsize=16, width=2.0, length=6)

    ax.spines["right"].set_visible(False)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_linewidth(2.0)
    ax.spines["bottom"].set_linewidth(2.0)

    _plot_top_annotations(ax, y_top=ax.get_ylim()[1])
    ax.legend(
        frameon=False,
        fontsize=16,
        loc="upper left",
        bbox_to_anchor=(1.01, 1.0),
        borderaxespad=0.0,
    )

    # Keep a wide plotting panel while reserving a right-side legend column.
    fig.subplots_adjust(left=0.09, right=0.73, bottom=0.12, top=0.86)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi)
    plt.close(fig)
    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Visualize grouped perifusion traces (mean with 95% CI per group)."
    )
    parser.add_argument("csv", help="Input trace CSV.")
    parser.add_argument("groups", help="Group assignment CSV.")
    parser.add_argument(
        "--out",
        default=None,
        help="Output PNG path (optional). Defaults to <input_stem>_grouped_trace.png",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Figure DPI.")
    parser.add_argument(
        "--y-upper",
        type=float,
        default=None,
        help="Optional fixed y-axis upper limit. If omitted, uses auto-scaling.",
    )
    parser.add_argument(
        "--y-scale",
        type=float,
        default=1.2,
        help="Auto y-axis multiplier applied to max raw/CI upper value (default: 1.2).",
    )
    args = parser.parse_args()

    output = visualize_grouped_trace_csv(
        csv_path=args.csv,
        group_csv_path=args.groups,
        output_path=args.out,
        dpi=args.dpi,
        y_upper=args.y_upper,
        y_scale=args.y_scale,
    )
    print(output)
