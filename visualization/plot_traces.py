"""
Utilities for visualizing perifusion traces from INS/GCG CSV files.
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Sequence, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

plt.rcParams["font.family"] = "Arial"

# Fixed stimulus layout (kept constant across datasets).
# Important convention:
# - "G 5.6" phases are background-only (no black bar)
# - All other labels are stimuli and get black bars
STIMULUS_SEGMENTS: List[Tuple[int, int, str]] = [
    (0, 12, "G 5.6"),
    (12, 42, "G 16.7"),
    (42, 63, "G 5.6"),
    (63, 72, "G 16.7\n+ IMBX 100"),
    (72, 93, "G 5.6"),
    (93, 102, "G 1.7\n+ Epi 1"),
    (102, 123, "G 5.6"),
    (123, 132, "KCl 20"),
    (132, 150, "G 5.6"),
]


def _infer_label_from_filename(csv_path: Path) -> str:
    stem = csv_path.stem.lower()

    if "ins" in stem:
        hormone = "ins"
    elif "gcg" in stem:
        hormone = "gcg"
    else:
        raise ValueError(
            f"Could not infer hormone type from file name: {csv_path.name}. "
            "Expected 'ins' or 'gcg' in file name."
        )

    if "ieq" in stem:
        mode = "ieq"
    elif "content" in stem:
        mode = "content"
    else:
        raise ValueError(
            f"Could not infer normalization from file name: {csv_path.name}. "
            "Expected 'ieq' or 'content' in file name."
        )

    if hormone == "ins" and mode == "ieq":
        return "Insulin secretion (ng/100 IEQ/min)"
    if hormone == "ins" and mode == "content":
        return "Insulin secretion (% content/min)"
    if hormone == "gcg" and mode == "ieq":
        return "Glucagon secretion (pg/100 IEQ/min)"
    return "Glucagon secretion (% content/min)"


def _prepare_trace_data(input_df: pd.DataFrame) -> Tuple[pd.Series, pd.DataFrame]:
    df = input_df.copy()
    df.columns = [str(col) for col in df.columns]

    time_cols = [col for col in df.columns if "time" in col.lower()]
    if not time_cols:
        raise KeyError("No column containing 'time' found in input data.")
    time_col = time_cols[0]

    donor_cols: List[str] = []
    for col in df.columns:
        lower_col = col.lower()
        if col == time_col:
            continue
        if lower_col.startswith("unnamed"):
            continue
        donor_cols.append(col)

    if not donor_cols:
        raise ValueError("No donor/sample columns found after filtering index columns.")

    time_values = pd.to_numeric(df[time_col], errors="coerce")
    traces = df[donor_cols].apply(pd.to_numeric, errors="coerce")

    valid_rows = time_values.notna()
    time_values = time_values[valid_rows].reset_index(drop=True)
    traces = traces[valid_rows].reset_index(drop=True)
    return time_values, traces


def _plot_top_stimulus_annotations(ax: plt.Axes, y_top: float) -> None:
    text_y = y_top * 1.04
    bar_y = y_top * 1.005
    bar_h = y_top * 0.025

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
                    zorder=6,
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
                zorder=7,
            )
        else:
            # Keep G 5.6 labels inside the plot area.
            ax.text(
                (start + end) / 2,
                y_top * 0.985,
                label,
                ha="center",
                va="top",
                fontsize=14,
                weight="bold",
                clip_on=True,
                zorder=7,
            )


def visualize_trace_csv(
    csv_path: str | Path,
    output_path: str | Path | None = None,
    show: bool = False,
    dpi: int = 300,
) -> Path:
    """
    Create a trace visualization from one perifusion CSV file.

    The figure keeps a fixed style:
    - all donor traces as light lines
    - mean trace and SEM shadow
    - fixed vertical guide lines
    - fixed top stimulus annotations
    - fixed glucose background windows
    """
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Input CSV not found: {csv_path}")

    input_df = pd.read_csv(csv_path)
    time_x, trace_df = _prepare_trace_data(input_df)
    y_label = _infer_label_from_filename(csv_path)

    if output_path is None:
        output_path = csv_path.with_name(f"{csv_path.stem}_trace.png")
    output_path = Path(output_path)

    y_mean = trace_df.mean(axis=1, skipna=True)
    y_sem = trace_df.sem(axis=1, skipna=True)
    y_max = np.nanmax(trace_df.to_numpy(dtype=float))
    if not np.isfinite(y_max) or y_max <= 0:
        y_max = 1.0

    fig, ax = plt.subplots(figsize=(8, 6))

    # Fixed pale-yellow windows for G 5.6 phases.
    for start, end, label in STIMULUS_SEGMENTS:
        if label == "G 5.6":
            ax.axvspan(start, end, color="#f7f5cf", alpha=0.7, zorder=0)

    # Fixed vertical guide lines.
    boundaries = sorted({segment[0] for segment in STIMULUS_SEGMENTS[1:]})
    for x in boundaries:
        ax.axvline(x=x, color="#d8d8d8", linestyle=":", linewidth=1.0, zorder=1)

    # All individual donor traces (light).
    colors = plt.cm.GnBu(np.linspace(0.45, 0.9, trace_df.shape[1]))
    for idx, col in enumerate(trace_df.columns):
        ax.plot(
            time_x,
            trace_df[col],
            color=colors[idx],
            alpha=0.35,
            linewidth=1.5,
            zorder=2,
        )

    # Mean +/- SEM shadow.
    ax.fill_between(
        time_x.to_numpy(),
        (y_mean - y_sem).to_numpy(),
        (y_mean + y_sem).to_numpy(),
        color="#6fd0c3",
        alpha=0.35,
        linewidth=0,
        zorder=3,
    )
    ax.plot(time_x, y_mean, color="#3fb6a8", linewidth=2.5, zorder=4)

    ax.set_xlim(0, 150)
    ax.set_ylim(0, y_max * 1.08)
    ax.set_xticks([0, 30, 60, 90, 120, 150])
    ax.set_xlabel("Time (min)", fontsize=16)
    ax.set_ylabel(y_label, fontsize=20)
    ax.tick_params(axis="both", labelsize=16, width=2.0, length=6)

    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.spines["left"].set_linewidth(2.0)
    ax.spines["bottom"].set_linewidth(2.0)

    _plot_top_stimulus_annotations(ax, y_top=ax.get_ylim()[1])

    fig.tight_layout(rect=(0, 0, 1, 0.90))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=dpi)

    if show:
        plt.show()
    else:
        plt.close(fig)
    return output_path


def visualize_many(
    csv_paths: Sequence[str | Path],
    output_dir: str | Path | None = None,
    dpi: int = 300,
) -> List[Path]:
    """
    Generate trace visualizations for multiple CSV files.
    """
    generated: List[Path] = []
    output_root = Path(output_dir) if output_dir is not None else None

    for csv_path in csv_paths:
        csv_path = Path(csv_path)
        out_path = (
            output_root / f"{csv_path.stem}_trace.png"
            if output_root is not None
            else None
        )
        generated.append(visualize_trace_csv(csv_path, out_path, show=False, dpi=dpi))
    return generated


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Visualize perifusion traces from one or more CSV files."
    )
    parser.add_argument("csv", nargs="+", help="Input CSV file(s).")
    parser.add_argument(
        "--outdir",
        default=None,
        help="Output directory for generated PNG files (optional).",
    )
    parser.add_argument("--dpi", type=int, default=300, help="Figure DPI.")
    args = parser.parse_args()

    outputs = visualize_many(args.csv, output_dir=args.outdir, dpi=args.dpi)
    for path in outputs:
        print(path)
