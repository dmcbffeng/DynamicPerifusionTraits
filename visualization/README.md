# Visualization Scripts

This folder contains two plotting scripts:

- `plot_traces.py`: one cohort mean trace (with SEM)
- `plot_grouped_traces.py`: one mean trace (with SEM) per user-defined group

Both scripts keep the fixed stimulation layout, vertical dotted boundaries, top annotations, and top horizontal boundary line.

## 1) Single-Cohort Plot (`plot_traces.py`)

### Default figure style (matches `example2.png`)

- mean line with dot markers
- shaded `mean +/- SEM`
- no individual donor traces by default
- yellow shading marks **stimulus phases** (not `G 5.6`)
- black top bars mark stimulus phases
- `G 5.6` labels stay inside the plot area

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

Output name pattern:

- `<input_stem>_trace.png`

## 2) Grouped Plot (`plot_grouped_traces.py`)

This script compares groups (for example, Healthy vs Diabetes) as separate mean+SEM lines.
Legend labels are shown as `group 1`, `group 2`, ... (with sample size), based on sorted group names.

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
  --out visualization/HIPP_ins_ieq_grouped_example.png
```

Output default (if `--out` is not given):

- `<input_stem>_grouped_trace.png`

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
