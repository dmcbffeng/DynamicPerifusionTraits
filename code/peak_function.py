"""
Pipeline for processing dynamic perifusion data of human isolated islets.

This module calculates features (traits) from insulin and glucagon secretion measurements,
including basal secretion, Area Under Curve (AUC), Stimulation Indices (SI), and
Inhibition Indices (II) under different stimuli.

Main functions:
    - parse_basal_secretion: Extract basal secretion from specified time ranges
    - parse_peak_and_baseline_region: Extract peak regions and baseline values
    - AUC_from_a_region: Calculate Area Under Curve for detected peaks
    - traits_for_all: Main function to calculate all traits for all donors
"""

import numpy as np
import pandas as pd
from typing import Tuple, List, Dict, Union
import matplotlib.pyplot as plt
plt.rcParams["font.family"] = "Arial"

# Constants
FLOAT_TOLERANCE = 1e-5  # Tolerance for floating point comparisons


def parse_basal_secretion(
        entire_x: pd.Series,
        entire_y: pd.Series,
        basal_range: str
) -> float:
    """
    Extract and calculate mean basal secretion from specified time ranges.

    Parses a time range string that can contain multiple ranges separated by '|'.
    Each range can be either:
    - A single time point: "30"
    - A time range: "3-9"
    - Multiple ranges: "3-9|30" (baseline from 3-9 minutes and at 30 minutes)

    Args:
        entire_x: Time points (in minutes) as a pandas Series
        entire_y: Secretion values corresponding to time points as a pandas Series
        basal_range: String specifying time ranges, e.g., "3-9" or "3-9|30"

    Returns:
        Mean basal secretion value (float)

    Example:
        >>> time_points = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> secretion = pd.Series([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4])
        >>> parse_basal_secretion(time_points, secretion, "3-9")
        1.0
    """
    time_points = []
    ranges = basal_range.split('|')
    for per_range in ranges:
        if '-' in per_range:
            start, end = per_range.split('-')
            start, end = int(start), int(end)
            time_points.extend(entire_x[(entire_x >= start) & (entire_x <= end)])
        else:
            time_point = int(per_range)
            time_points.extend(entire_x[(entire_x == time_point)])

    y_basal = entire_y[entire_x.isin(time_points)]
    return np.mean(y_basal)


def parse_peak_and_baseline_region(
        entire_x: pd.Series,
        entire_y: pd.Series,
        peak_range: str,
        baseline_points: str,
        negative_peak: bool
) -> Tuple[np.ndarray, np.ndarray, float]:
    """
    Extract peak region and baseline, then correct the curve by subtracting baseline.

    This function:
    1. Identifies baseline time points from the baseline_points string
    2. Calculates mean baseline value
    3. Extracts the peak region from peak_range
    4. Corrects the curve by subtracting baseline (or vice versa for negative peaks)

    Args:
        entire_x: Time points (in minutes) as a pandas Series
        entire_y: Secretion values corresponding to time points as a pandas Series
        peak_range: Time range for peak region, must be in format "start-end" (e.g., "9-63")
        baseline_points: Time points/ranges for baseline calculation (e.g., "3-9" or "3-9|30")
        negative_peak: If True, treats the peak as a negative peak (inhibition).
                      For negative peaks, corrected_curve = baseline - curve.
                      For positive peaks, corrected_curve = curve - baseline.

    Returns:
        Tuple containing:
        - x_curve: Time points within the peak range as numpy array
        - corrected_curve: Baseline-corrected secretion values as numpy array
        - y_baseline: Mean baseline value (float)

    Example:
        >>> time_points = pd.Series([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        >>> secretion = pd.Series([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4])
        >>> x, y, baseline = parse_peak_and_baseline_region(
        ...     time_points, secretion, "5-8", "1-3", False
        ... )
        >>> baseline  # Mean of values at time 1-3
        0.6
    """
    # Get baseline points
    baseline_time_points = []
    ranges = baseline_points.split('|')
    for per_range in ranges:
        if '-' in per_range:
            start, end = per_range.split('-')
            start, end = int(start), int(end)
            baseline_time_points.extend(entire_x[(entire_x >= start) & (entire_x <= end)])
        else:
            time_point = int(per_range)
            baseline_time_points.extend(entire_x[entire_x == time_point])
    
    y_baseline = np.mean(entire_y[entire_x.isin(baseline_time_points)])

    # Peak must be a single range "a-b"
    start, end = peak_range.split('-')
    start, end = int(start), int(end)
    x_curve = np.array(entire_x[(entire_x >= start) & (entire_x <= end)])
    y_curve = np.array(entire_y[(entire_x >= start) & (entire_x <= end)])

    # Correct curve by subtracting baseline
    if negative_peak:
        corrected_curve = y_baseline - y_curve
    else:
        corrected_curve = y_curve - y_baseline
    
    return x_curve, corrected_curve, y_baseline


def AUC_from_a_region(
    x_curve: np.ndarray,
    y_corrected_curve: np.ndarray,
    y_baseline: float,
    min_height_ratio: float = 0.10,
    min_peak_length: int = 3
) -> Tuple[List[Union[int, float]], List[Tuple[float, float, float, float, float, float]]]:
    """
    Calculate Area Under Curve (AUC) from a baseline-corrected secretion curve.

    This function:
    1. Identifies peak regions (continuous positive values above threshold)
    2. Filters peaks by minimum length and relative height
    3. Calculates AUC for each peak using trapezoidal integration
    4. Interpolates peak boundaries for more accurate start/end times

    Args:
        x_curve: Time points (in minutes) as numpy array
        y_corrected_curve: Baseline-corrected secretion values as numpy array
        y_baseline: Baseline value used for correction (for reference)
        min_height_ratio: Minimum peak height relative to maximum value in curve.
                         Peaks with height < min_height_ratio * max(y_corrected_curve) are filtered out.
                         Default: 0.10 (10% of maximum)
        min_peak_length: Minimum number of consecutive points required to define a peak.
                        Default: 3

    Returns:
        Tuple containing:
        - summary: List of summary statistics [N_peaks, total_area, baseline, max_height]
          where:
          * N_peaks: Number of detected peaks
          * total_area: Sum of AUCs from all peaks
          * baseline: Baseline value (y_baseline)
          * max_height: Maximum peak height across all peaks
        - peak_info: List of tuples, each containing (start_x, end_x, peak_x, peak_y, auc, baseline)
          where:
          * start_x: Interpolated start time of peak
          * end_x: Interpolated end time of peak
          * peak_x: Time point of peak maximum
          * peak_y: Peak height (maximum value)
          * auc: Area under curve for this peak
          * baseline: Baseline value

    Notes:
        - Peaks are defined as continuous regions where y_corrected_curve > FLOAT_TOLERANCE
        - Peak boundaries are interpolated to find exact intersection with zero
        - Uses trapezoidal rule for AUC calculation

    Example:
        >>> x = np.array([1, 2, 3, 4, 5, 6, 7])
        >>> y = np.array([0, 0, 1, 2, 1, 0, 0])
        >>> summary, peaks = AUC_from_a_region(x, y, 0.0, min_height_ratio=0.1, min_peak_length=3)
        >>> summary[0]  # Number of peaks
        1
        >>> summary[1]  # Total AUC
        4.0
    """
    peak_info = []
    summary = [0, 0, y_baseline, 0]  # [N_peaks, total_area, baseline, max_height]

    # Find all peak regions, filter by length
    # A peak is defined as a continuous region of positive values
    # "0 - positive - positive - 0" would not be calculated as a peak if min_peak_length=3
    peak_regions = []
    peak_start = None
    for i in range(len(y_corrected_curve)):
        if y_corrected_curve[i] > FLOAT_TOLERANCE:  # Avoid float number issues
            if peak_start is None:
                peak_start = i  # Start of a peak
        else:
            if peak_start is not None:
                if i - peak_start >= min_peak_length:
                    peak_regions.append((peak_start, i - 1))
                peak_start = None
    
    # Handle peak that extends to the end of the curve
    if peak_start is not None and len(y_corrected_curve) - peak_start >= min_peak_length:
        peak_regions.append((peak_start, len(y_corrected_curve) - 1))

    # Filter peaks by relative height and calculate AUC for each peak
    max_curve_value = max(y_corrected_curve) if len(y_corrected_curve) > 0 else 0
    
    for start_idx, end_idx in peak_regions:
        # Find peak maximum
        peak_region_values = y_corrected_curve[start_idx: end_idx + 1]
        height = np.max(peak_region_values)
        loc_height = np.argmax(peak_region_values) + start_idx
        peak_x = x_curve[loc_height]
        
        # Filter by relative height
        if height < min_height_ratio * max_curve_value:
            continue

        # Calculate AUC using trapezoidal rule
        auc = 0.0
        for i in range(start_idx, end_idx):
            auc += (x_curve[i + 1] - x_curve[i]) * (y_corrected_curve[i] + y_corrected_curve[i + 1]) / 2

        # Interpolate accurate start location (where curve crosses zero)
        if start_idx == 0:
            peak_st = x_curve[start_idx]
        else:
            # Linear interpolation to find zero crossing
            dx = x_curve[start_idx] - x_curve[start_idx - 1]
            dy = y_corrected_curve[start_idx] - y_corrected_curve[start_idx - 1]
            if abs(dy) > FLOAT_TOLERANCE:
                peak_st = x_curve[start_idx] - dx * y_corrected_curve[start_idx] / dy
                # Add partial AUC from interpolated start to first point
                auc += (x_curve[start_idx] - peak_st) * y_corrected_curve[start_idx] / 2
            else:
                peak_st = x_curve[start_idx]

        # Interpolate accurate end location (where curve crosses zero)
        if end_idx == len(y_corrected_curve) - 1:
            peak_ed = x_curve[end_idx]
        else:
            # Linear interpolation to find zero crossing
            dx = x_curve[end_idx + 1] - x_curve[end_idx]
            dy = y_corrected_curve[end_idx + 1] - y_corrected_curve[end_idx]
            if abs(dy) > FLOAT_TOLERANCE:
                peak_ed = x_curve[end_idx] + dx * y_corrected_curve[end_idx] / abs(dy)
                # Add partial AUC from last point to interpolated end
                auc += (peak_ed - x_curve[end_idx]) * y_corrected_curve[end_idx] / 2
            else:
                peak_ed = x_curve[end_idx]

        peak_info.append((peak_st, peak_ed, peak_x, height, auc, y_baseline))
        summary[0] += 1  # Increment peak count
        summary[1] += auc  # Add to total area
        if height > summary[3]:
            summary[3] = height  # Update max height

    return summary, peak_info


def traits_for_all(
    input_df: pd.DataFrame,
    parameter_df: pd.DataFrame,
    trait_prefix: str = 'GCG-IEQ'
) -> pd.DataFrame:
    """
    Calculate traits (basal secretion, AUCs, SIs, IIs) for all donors and all experimental phases.

    This is the main function that processes perifusion data for multiple donors and calculates:
    - Basal secretion: Mean secretion during baseline periods
    - AUC (Area Under Curve): Total area under secretion peaks
    - SI (Stimulation Index): Ratio of peak maximum to baseline (for positive peaks)
    - II (Inhibition Index): Ratio of baseline to valley minimum (for negative peaks)

    Args:
        input_df: Input pandas DataFrame with:
                 - One column containing 'time' (case-insensitive) with time points in minutes
                 - Other columns: one per donor, containing secretion values over time
        parameter_df: Parameter DataFrame with required columns:
                     - PeakName: Name of the peak/baseline phase (e.g., "G 16.7", "Basal Secretion")
                     - PeakRange: Time range for peak region (e.g., "9-63") or baseline range
                     - BaselineTime: Time points/ranges for baseline calculation (e.g., "3-9")
                     - MinHeightRatio: Minimum peak height ratio (0-1) for peak detection
                     - MinPeakLength: Minimum number of points required for a peak
                     - BaselineOrPeak: Either "Baseline" or "Peak"
                     - NegativePeak: Boolean, True for inhibition (negative) peaks, False for stimulation peaks
                     - CalculateSIorII: Boolean, whether to calculate Stimulation/Inhibition Index
        trait_prefix: Prefix for trait names in output (e.g., "GCG-IEQ", "INS-content")
                     Default: 'GCG-IEQ'

    Returns:
        DataFrame with columns:
        - Donor ID: List of donor identifiers
        - For each phase in parameter_df:
          * "{trait_prefix} {PeakName}": Basal secretion (if BaselineOrPeak == "Baseline")
          * "{trait_prefix} {PeakName} AUC": Area under curve (if BaselineOrPeak == "Peak")
          * "{trait_prefix} {PeakName} SI": Stimulation Index (if CalculateSIorII == True and NegativePeak == False)
          * "{trait_prefix} {PeakName} II": Inhibition Index (if CalculateSIorII == True and NegativePeak == True)

    Raises:
        AssertionError: If required columns are missing from parameter_df
        KeyError: If no time column is found in input_df

    Example:
        >>> import pandas as pd
        >>> input_data = pd.DataFrame({
        ...     'time': [1, 2, 3, 4, 5],
        ...     'Donor1': [0.5, 0.6, 0.7, 0.8, 0.9],
        ...     'Donor2': [0.4, 0.5, 0.6, 0.7, 0.8]
        ... })
        >>> params = pd.DataFrame({
        ...     'PeakName': ['Basal Secretion'],
        ...     'PeakRange': ['1-3'],
        ...     'BaselineTime': ['1-3'],
        ...     'MinHeightRatio': [0.0],
        ...     'MinPeakLength': [0],
        ...     'BaselineOrPeak': ['Baseline'],
        ...     'NegativePeak': [False],
        ...     'CalculateSIorII': [False]
        ... })
        >>> result = traits_for_all(input_data, params, 'TEST')
        >>> result.columns
        Index(['Donor ID', 'TEST Basal Secretion'], dtype='object')
    """
    # Get all column names - identify Time column and donor IDs
    input_df.columns = input_df.columns.astype(str)
    all_cols = input_df.columns
    time_col_name = [col for col in all_cols if 'time' in col.lower()]
    if not time_col_name:
        raise KeyError("No column containing 'time' found in input_df")
    time_col_name = time_col_name[0]
    time_x = input_df[time_col_name]
    donors = [col for col in all_cols if col != time_col_name]

    # Validate parameter DataFrame columns
    required_columns = [
        'PeakName', 'PeakRange', 'BaselineTime', 'MinHeightRatio', 'MinPeakLength',
        'BaselineOrPeak', 'NegativePeak', 'CalculateSIorII'
    ]
    missing_columns = [col for col in required_columns if col not in parameter_df.columns]
    if missing_columns:
        raise AssertionError(f"Missing required columns in parameter_df: {missing_columns}")

    all_results = {
        'Donor ID': donors,
    }

    # Process each phase defined in parameter_df
    for _, row in parameter_df.iterrows():
        if row['BaselineOrPeak'].lower() == 'baseline':
            # Calculate basal secretion
            results = []
            for donor in donors:
                if input_df[donor].hasnans:
                    results.append(pd.NA)
                else:
                    basal = parse_basal_secretion(time_x, input_df[donor], row['BaselineTime'])
                    results.append(basal)
            trait_name = f'{trait_prefix} {row["PeakName"]}'
            all_results[trait_name] = results
        else:
            # Calculate AUC and optionally SI/II
            results = []
            si_or_ii = []
            for donor in donors:
                if input_df[donor].hasnans:
                    results.append(pd.NA)
                    si_or_ii.append(pd.NA)
                else:
                    # Extract peak region and correct for baseline
                    sub_x, sub_y, y_baseline = parse_peak_and_baseline_region(
                        time_x, input_df[donor], row["PeakRange"],
                        row["BaselineTime"], bool(row["NegativePeak"])
                    )
                    
                    # Calculate AUC
                    summary, _ = AUC_from_a_region(
                        sub_x, sub_y, y_baseline,
                        min_height_ratio=row["MinHeightRatio"],
                        min_peak_length=int(row["MinPeakLength"]),
                    )
                    _, total_area, baseline, _ = summary
                    results.append(total_area)

                    # Calculate Stimulation Index (SI) or Inhibition Index (II)
                    max_height = np.max(sub_y) if np.max(sub_y) > 0 else 0
                    if bool(row["NegativePeak"]):
                        # For negative peaks: II = baseline / valley_min
                        valley_min = baseline - max_height
                        si = baseline / valley_min if valley_min * baseline > 0 else pd.NA
                    else:
                        # For positive peaks: SI = peak_max / baseline
                        peak_max = baseline + max_height
                        si = peak_max / baseline if baseline > 0 else pd.NA
                    si_or_ii.append(si)
            
            # Add AUC trait
            trait_name = f'{trait_prefix} {row["PeakName"]} AUC'
            all_results[trait_name] = results
            
            # Add SI or II trait if requested
            if bool(row["CalculateSIorII"]):
                trait_name = f'{trait_prefix} {row["PeakName"]} '
                if bool(row["NegativePeak"]):
                    trait_name += 'II'  # Inhibition Index
                else:
                    trait_name += 'SI'  # Stimulation Index
                all_results[trait_name] = si_or_ii

    return pd.DataFrame(all_results)


if __name__ == '__main__':
    # Example usage - process GCG-IEQ data
    inpt_df = pd.read_excel('../../01_HPAP_Data_Integration/20240424_HPAP_Master_Fan.xlsx', sheet_name='GCG-IEQ')
    inpt_df.drop(['Fraction', 'Stimulus'], axis=1, inplace=True)
    cols = list(inpt_df.columns)[:2]
    inpt_df = inpt_df[cols]

    param_df = pd.read_csv('../parameter/GCG_IEQ_parameter.csv')

    res = traits_for_all(
        inpt_df, param_df, trait_prefix='GCG-IEQ'
    )
    res.to_csv('../output/example_GCG.csv', index=False)

