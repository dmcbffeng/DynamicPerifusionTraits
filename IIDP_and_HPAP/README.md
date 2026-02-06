# Dynamic Perifusion Data — Human Islets (HIPP)

## What is dynamic perifusion data?

**Perifusion** is an ex vivo assay in which isolated islets are perfused with solution in a flow chamber while the effluent is collected over time. **Dynamic** perifusion means the perfusate composition is changed during the run (e.g., step changes in glucose, addition of drugs), so hormone secretion is measured as a **time series** in response to those stimuli. This yields secretion *rates* (e.g., ng/min or pg/min) at each time point rather than a single static value, and allows characterization of stimulus–secretion coupling (e.g., first- and second-phase insulin release, suppression of glucagon by glucose).

This folder contains dynamic perifusion data from human isolated islets, processed for the Human Islet Phenotyping Program (HIPP).

---

## 1. Summary

- **Donor Information**: `20260202_HIPP_Report.xlsx`.
- **Raw Data (50 time points)**: `HIPP_ins_{normalization}.csv`, `HIPP_gcg_{normalization}.csv`.
- **Features (traits)**: `HIPP_all_traits.csv`. Trait definitions follow the scheme illustrated in `F2.large.jpg`.
- **Donor ID**: Each sample is labeled by **RRID** (e.g. `RRID:SAMN08769199`). Where available, **HPAP ID** is given in `HIPP_all_traits.csv`.


---

## 2. Normalization (Raw Time-Series)

Values in the `*_ieq.csv` and `*_content.csv` files are the same functional data normalized with two different methods.

- **IEQ (islet equivalent)**: Secretion rate **per 100 IEQ** (insulin: ng/100 IEQ/min; glucagon: pg/100 IEQ/min). Islet Equivalent (IEQ) is defined as the mass of an islet with a diameter of 150 μm, assuming that islets are spherical. This allows comparison across donors with different islet amounts.
- **Content**: Secretion rate as **% of total hormone content** (as measured in the assay). Reflects fractional release relative to total content.

If we have to choose one to visualize, choose **IEQ**.

---

## 3. Trait (Feature) Definitions

Traits are computed from the time-series using fixed **time windows** and baseline regions. For each phase, the pipeline:

1. Takes secretion in the phase window and subtracts a **baseline** (mean over a defined baseline period).
2. Detects peaks (positive or negative) in the baseline-corrected curve.
3. Computes **AUC** (trapezoidal rule), and where applicable **SI** or **II**.

### 3.1 Trait types

- **Basal Secretion**  
  Mean secretion over the **baseline period** (e.g. 3–9 min). No baseline subtraction; same units as the raw series (IEQ or content).

- **AUC (Area Under Curve)**  
  Area under the **baseline-corrected** secretion curve in the phase window.  
  - For **stimulation** (positive peaks): corrected curve = secretion − baseline.  
  - For **inhibition** (negative peaks, e.g. high glucose suppressing glucagon): corrected curve = baseline − secretion.  
  Units: (secretion unit) × min (e.g. ng/100 IEQ/min × min for INS-IEQ).

- **SI (Stimulation Index)**  
  For **positive** peaks: **peak maximum / baseline**. Dimensionless.

- **II (Inhibition Index)**  
  For **negative** peaks (inhibition): **baseline / valley minimum**. Dimensionless.

Missing or invalid values (e.g. no peak detected, zero baseline) are set to **NA** in `HIPP_all_traits.csv`.

### 3.2 Experimental phases (time in minutes)

Approximate protocol timeline and how it maps to trait names:

| Phase | Approx. time | Description | Typical use in traits |
|-------|----------------|-------------|-------------------------|
| **Basal** | 3–9 | Low glucose baseline | Basal secretion |
| **G 16.7** | 9–60 (INS) / 9–63 (GCG) | High glucose (16.7 mM) | AUC, SI or II |
| **G 16.7 phase 1** | 9–24 | First phase of high glucose (INS only) | AUC |
| **G 16.7 phase 2** | 24–60 | Second phase of high glucose (INS only) | AUC |
| **G 16.7+IMBX** | 63–90 (INS) / 69–90 (GCG) | High glucose + phosphodiesterase inhibitor | AUC, SI |
| **G 1.7+Epi** | 93–120 (INS) / 93–117 (GCG) | Low glucose + epinephrine | AUC, SI or II |
| **KCl 20** | 120–150 (INS) / 120–144 (GCG) | KCl depolarization | AUC, SI |

Exact windows and baseline definitions are set in the pipeline’s parameter files (not in this folder). Column names in `HIPP_all_traits.csv` (e.g. `INS-IEQ G 16.7 AUC`, `GCG-IEQ G 16.7 II`) refer to these phases.

---

## 4. Structure of `HIPP_all_traits.csv`

- **Rows**: One per donor (RRID).
- **Columns**:
  - `Donor ID`: RRID.
  - `HPAP ID`: HPAP donor ID when available; otherwise empty.
  - Then blocks of traits:
    - **INS-IEQ**: Basal Secretion, G 16.7 (AUC, SI), G 16.7 phase 1/2 AUC, G 16.7+IMBX (AUC, SI), G 1.7+Epi (AUC, II), KCl 20 (AUC, SI).
    - **INS-content**: Basal Secretion, AUCs for the same phases (no SI/II in this export).
    - **GCG-IEQ**: Basal Secretion, G 16.7 (AUC, II), G 16.7+IMBX (AUC, SI), G 1.7+Epi (AUC, SI), KCl 20 (AUC, SI).
    - **GCG-content**: Basal Secretion, AUCs for the same phases.

Numeric traits are in the units described above; SI and II are dimensionless. Treat **NA** as missing values in downstream analysis.

---

## 5. Raw Time-Series CSVs (`*_ieq.csv`, `*_content.csv`)

- **Column 1**: Unnamed index (row number).
- **Column 2**: `time` (minutes).
- **Remaining columns**: One per donor; column name = RRID (e.g. `RRID:SAMN08769199`). Values are secretion rates in the unit of that file (see Section 2).

Time points are shared across donors; missing or invalid measurements may appear as blank or NaN depending on the export.

---

## 6. Contact

For questions about the data or trait definitions: **Fan Feng** (fan.feng@vumc.org and ccmeffeng@gmail.com).
