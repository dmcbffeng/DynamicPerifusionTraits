# Visualization Scripts

This folder contains two plotting scripts:

- `plot_traces.py`: one cohort mean trace (with 95% CI)
- `plot_grouped_traces.py`: one mean trace (with 95% CI) per user-defined group

Both scripts keep the fixed stimulation layout, vertical dotted boundaries, top annotations, and top horizontal boundary line.

## 1) Single-Cohort Plot (`plot_traces.py`)

### Default figure style (matches `example2.png`)

- mean line with dot markers
- shaded `mean +/- 95% CI` (`mean +/- 1.96 * SEM`)
- no individual donor traces by default
- yellow shading marks **stimulus phases** (not `G 5.6`)
- black top bars mark stimulus phases
- `G 5.6` labels stay inside the plot area
- y-axis auto range uses `--y-scale` times max(data, CI upper); default `1.2x`

### Y-axis label inference from filename

- `ins` + `ieq` -> `Insulin secretion (ng/100 IEQ/min)`
- `ins` + `content` -> `Insulin secretion (% content/min)`
- `gcg` + `ieq` -> `Glucagon secretion (pg/100 IEQ/min)`
- `gcg` + `content` -> `Glucagon secretion (% content/min)`

Ensure those keywords are in the CSV filename.

### Usage

```bash
python visualization/plot_traces.py visualization/HIPP_ins_ieq.csv --outdir visualization
```

Multiple files:

```bash
python visualization/plot_traces.py \
  visualization/HIPP_ins_ieq.csv \
  visualization/HIPP_gcg_ieq.csv \
  --outdir visualization
```

Optional:

- `--show-individual-traces`: overlay all donor traces
- `--dpi <int>`: figure DPI (default `300`)
- `--y-upper <float>`: fixed y-axis upper limit (overrides auto-scale)
- `--y-scale <float>`: auto y-axis multiplier (default `1.2`)

Output name pattern:

- `<input_stem>_trace.png`

## 2) Grouped Plot (`plot_grouped_traces.py`)

This script compares groups (for example, Healthy vs Diabetes) as separate mean+95% CI lines.
Legend labels use the actual group names from the assignment CSV (with sample size).

### Group assignment input

Provide a CSV with two columns:

- donor/sample id column (name can include `donor`, `rrid`, or `sample`)
- group column (name includes `group`)

Example file included:

- `visualization/example_group_assignments.csv`

Example contents:

```csv
donor_id,group
RRID:SAMN08769199,Healthy
RRID:SAMN08769090,Diabetes
```

### Usage

```bash
python visualization/plot_grouped_traces.py \
  visualization/HIPP_ins_ieq.csv \
  visualization/example_group_assignments.csv \
  --out visualization/HIPP_ins_ieq_grouped_example.png \
  --y-scale 1.2
```

Output default (if `--out` is not given):

- `<input_stem>_grouped_trace.png`

Optional grouped flags:

- `--y-upper <float>`: fixed y-axis upper limit (overrides auto-scale)
- `--y-scale <float>`: auto y-axis multiplier (default `1.2`)
- `--group-colors <spec>`: custom group colors, either positional (`#0072B2,#D55E00,#009E73`) or explicit mapping (`Healthy:#0072B2,Diabetes:#D55E00,Obese:#009E73`)

## Python API

```python
from visualization.plot_traces import visualize_trace_csv
from visualization.plot_grouped_traces import visualize_grouped_trace_csv

visualize_trace_csv("visualization/HIPP_ins_ieq.csv")

visualize_grouped_trace_csv(
    csv_path="visualization/HIPP_ins_ieq.csv",
    group_csv_path="visualization/example_group_assignments.csv",
    output_path="visualization/HIPP_ins_ieq_grouped_example.png",
)
```
