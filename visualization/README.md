# Visualization Script

This folder contains a plotting script to generate perifusion trace figures from CSV files.

## Script

- `plot_traces.py`

## What It Generates

For each input CSV, the script creates one PNG figure with:

- individual donor traces (light lines)
- mean trace (bold line)
- mean +/- SEM shadow
- fixed background windows, vertical lines, and top annotations

## Y-Axis Label Rules

The y-axis label is inferred from the input filename:

- contains `ins` + `ieq` -> `Insulin secretion (ng/100 IEQ/min)`
- contains `ins` + `content` -> `Insulin secretion (% content/min)`
- contains `gcg` + `ieq` -> `Glucagon secretion (pg/100 IEQ/min)`
- contains `gcg` + `content` -> `Glucagon secretion (% content/min)`

Make sure input filenames include those keywords (for example, `HIPP_ins_ieq.csv`).

## Usage

From the repository root:

```bash
python visualization/plot_traces.py visualization/HIPP_ins_ieq.csv --outdir visualization
```

Multiple files at once:

```bash
python visualization/plot_traces.py \
  visualization/HIPP_ins_ieq.csv \
  visualization/HIPP_gcg_ieq.csv \
  visualization/HIPP_ins_content.csv \
  visualization/HIPP_gcg_content.csv \
  --outdir visualization
```

## Output Naming

Each output file is named:

- `<input_stem>_trace.png`

Examples:

- `HIPP_ins_ieq.csv` -> `HIPP_ins_ieq_trace.png`
- `HIPP_gcg_content.csv` -> `HIPP_gcg_content_trace.png`

## Optional Arguments

- `--outdir <dir>`: output directory (default: same directory as each input file)
- `--dpi <int>`: figure DPI (default: `300`)

## Python API (Optional)

You can also import and call from Python:

```python
from visualization.plot_traces import visualize_trace_csv, visualize_many

visualize_trace_csv("visualization/HIPP_ins_ieq.csv")
visualize_many(
    ["visualization/HIPP_ins_ieq.csv", "visualization/HIPP_gcg_ieq.csv"],
    output_dir="visualization",
)
```
