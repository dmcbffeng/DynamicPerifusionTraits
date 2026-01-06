# TracePipeline: Dynamic Perifusion Data Analysis Pipeline

This pipeline processes dynamic perifusion data from human isolated islets to calculate quantitative traits (features) from insulin (INS) and glucagon (GCG) secretion measurements under different stimuli.

## Overview

The pipeline analyzes time-series secretion data and extracts the following traits:

- **Basal Secretion**: Mean secretion during baseline periods
- **AUC (Area Under Curve)**: Total area under secretion peaks, calculated using trapezoidal integration
- **SI (Stimulation Index)**: Ratio of peak maximum to baseline (for positive peaks)
- **II (Inhibition Index)**: Ratio of baseline to valley minimum (for negative/inhibition peaks)

These traits are calculated for multiple experimental phases (e.g., glucose stimulation, KCl stimulation) across all donors in your dataset.

## Requirements

- Python 3.7+
- Required packages:
  - `numpy`
  - `pandas`
  - `scipy`
  - `matplotlib`
  - `openpyxl` (for reading Excel files)

Install dependencies:
```bash
pip install numpy pandas scipy matplotlib openpyxl
```

## Repository Structure

```
TracePipeline2/
├── code/
│   └── peak_function.py          # Main analysis functions
├── parameter/
│   ├── GCG_IEQ_parameter.csv     # Parameters for GCG IEQ analysis
│   ├── GCG_content_parameter.csv  # Parameters for GCG content analysis
│   ├── INS_IEQ_parameter.csv     # Parameters for INS IEQ analysis
│   └── INS_content_parameter.csv # Parameters for INS content analysis
├── data/
│   └── [Your data files]         # Input Excel/CSV files
└── output/
    └── [Output CSV files]        # Calculated traits
```

## Understanding Parameter Files

Parameter files (CSV format) define the experimental phases and analysis settings. Each row represents one phase or baseline period to analyze.

### Required Columns

| Column | Description | Example Values |
|--------|-------------|----------------|
| `PeakName` | Name of the phase/baseline | "Basal Secretion", "G 16.7", "KCl 20" |
| `PeakRange` | Time range for peak region (minutes) | "9-63", "120-144" |
| `BaselineTime` | Time points/ranges for baseline calculation | "3-9", "3-9\|30", "69\|90" |
| `MinHeightRatio` | Minimum peak height relative to max (0-1) | 0.1, 0.03 |
| `MinPeakLength` | Minimum consecutive points for a peak | 3, 6 |
| `BaselineOrPeak` | Type: "Baseline" or "Peak" | "Baseline", "Peak" |
| `NegativePeak` | Boolean: True for inhibition, False for stimulation | True, False |
| `CalculateSIorII` | Boolean: Whether to calculate SI/II | True, False |

### Time Range Format

The `BaselineTime` and `PeakRange` columns accept time specifications in the following formats:

- **Single time point**: `"30"` (at 30 minutes)
- **Time range**: `"3-9"` (from 3 to 9 minutes, inclusive)
- **Multiple ranges**: `"3-9|30"` (from 3-9 minutes AND at 30 minutes)
- **Multiple points**: `"69|90"` (at 69 minutes AND at 90 minutes)

### Example Parameter File

```csv
PeakName,PeakRange,BaselineTime,MinHeightRatio,MinPeakLength,BaselineOrPeak,NegativePeak,CalculateSIorII
Basal Secretion,3-9,3-9,0,0,Baseline,False,False
G 16.7,9-63,3-9,0.03,6,Peak,True,True
G 16.7+IMBX,69-90,69|90,0.1,3,Peak,False,True
KCl 20,120-144,120|144,0.1,3,Peak,False,True
```

**Explanation:**
- **Row 1**: Calculate basal secretion from 3-9 minutes
- **Row 2**: Analyze peak from 9-63 minutes (negative peak, inhibition), baseline from 3-9 minutes, calculate II
- **Row 3**: Analyze peak from 69-90 minutes, baseline at 69 and 90 minutes, calculate SI
- **Row 4**: Analyze peak from 120-144 minutes, baseline at 120 and 144 minutes, calculate SI

## Preparing Input Data

### Data Format

Your input data should be a pandas DataFrame (or CSV/Excel file that can be read into one) with the following structure:

- **One column** containing time points (in minutes). The column name must contain the word "time" (case-insensitive).
- **Additional columns**, one per donor/sample, containing secretion values over time.

### Example Input Data Structure

| time | Donor1 | Donor2 | Donor3 | ... |
|------|--------|--------|--------|-----|
| 3    | 0.5    | 0.4    | 0.6    | ... |
| 6    | 0.6    | 0.5    | 0.7    | ... |
| 9    | 0.7    | 0.6    | 0.8    | ... |
| ...  | ...    | ...    | ...    | ... |

### Data Requirements

1. **Time column**: Must be numeric and monotonically increasing
2. **Secretion columns**: Should contain numeric values. Missing values (NaN) are handled automatically (result will be `pd.NA`)
3. **Consistent sampling**: Time points should be consistent across all donors

### Loading Data from Excel

If your data is in Excel format, you can load it like this:

```python
import pandas as pd

# Read from Excel
data = pd.read_excel('path/to/your/data.xlsx', sheet_name='Sheet1')

# Remove unnecessary columns if needed
data = data.drop(['Fraction', 'Stimulus'], axis=1)

# Ensure time column is named appropriately
data.columns = ['time'] + [list of donor names]
```

## Using the Functions

### Main Function: `traits_for_all()`

This is the primary function you'll use to calculate all traits for all donors.

```python
from peak_function import traits_for_all
import pandas as pd

# Load your data
input_df = pd.read_csv('your_data.csv')  # or pd.read_excel(...)

# Load parameter file
parameter_df = pd.read_csv('parameter/your_parameter_file.csv')

# Calculate traits
results = traits_for_all(
    input_df=input_df,
    parameter_df=parameter_df,
    trait_prefix='INS-IEQ'  # Prefix for output column names
)

# Save results
results.to_csv('output/traits.csv', index=False)
```

### Function Parameters

- **`input_df`** (pd.DataFrame): Your secretion data with time column and donor columns
- **`parameter_df`** (pd.DataFrame): Parameter file loaded as DataFrame
- **`trait_prefix`** (str, optional): Prefix for trait names in output. Default: `'GCG-IEQ'`

### Output Format

The function returns a DataFrame with:

- **`Donor ID`** column: List of all donor identifiers
- **Trait columns**: One column per phase defined in the parameter file:
  - `{trait_prefix} {PeakName}`: Basal secretion values
  - `{trait_prefix} {PeakName} AUC`: Area under curve values
  - `{trait_prefix} {PeakName} SI`: Stimulation Index values (if calculated)
  - `{trait_prefix} {PeakName} II`: Inhibition Index values (if calculated)

### Example Output

| Donor ID | INS-IEQ Basal Secretion | INS-IEQ G 16.7 AUC | INS-IEQ G 16.7 SI | ... |
|----------|------------------------|-------------------|------------------|-----|
| Donor1   | 0.65                  | 45.2              | 2.3              | ... |
| Donor2   | 0.58                  | 38.7              | 2.1              | ... |
| ...      | ...                   | ...               | ...              | ... |

## Complete Example

Here's a complete example script:

```python
"""
Example: Processing insulin secretion data
"""
import pandas as pd
from peak_function import traits_for_all

# 1. Load your data
data = pd.read_excel(
    'data/your_data.xlsx',
    sheet_name='INS IEQ',
    skiprows=1
)
data.drop(['Fraction', 'Stimulus'], axis=1, inplace=True)
data.columns = ['time'] + ['Donor1', 'Donor2', 'Donor3']  # Adjust as needed

# 2. Load parameter file
params = pd.read_csv('parameter/INS_IEQ_parameter.csv')

# 3. Calculate traits
results = traits_for_all(
    input_df=data,
    parameter_df=params,
    trait_prefix='INS-IEQ'
)

# 4. Save results
results.to_csv('output/INS_IEQ_traits.csv', index=False)
print(f"Processed {len(results)} donors")
print(f"Calculated {len(results.columns) - 1} traits")
```

## Example Usage Files

Example usage scripts are provided in the `/code` directory that demonstrate how to use the pipeline:

- **`cal_ins_traits_t1d_ctrl_20260106.py`**: Processes insulin (INS) secretion data for T1D and control donors
- **`cal_gcg_traits_t1d_ctrl_20260106.py`**: Processes glucagon (GCG) secretion data for T1D and control donors

These example scripts:
- Read data from `/data/T1D vs Ctrls.xlsx`
- Use parameter files from `/parameter/` directory
- Output results to `/output/` directory as CSV files

You can use these scripts as templates for your own analyses by modifying the data file paths, parameter files, and output locations as needed.

## Troubleshooting

### Common Issues

1. **"No column containing 'time' found"**
   - Ensure your time column name contains the word "time" (case-insensitive)

2. **"Missing required columns in parameter_df"**
   - Check that your parameter file has all 8 required columns (see "Understanding Parameter Files" section)

3. **Division by zero errors in SI/II calculation**
   - This is handled automatically (returns `pd.NA`), but check your baseline values if many donors have NA

4. **No peaks detected**
   - Check that `MinHeightRatio` and `MinPeakLength` are not too restrictive
   - Verify that your peak ranges contain actual secretion data

## Citation

[Placeholder]

## License

[Placeholder]

## Contact

Fan Feng, fan.feng@vumc.org

