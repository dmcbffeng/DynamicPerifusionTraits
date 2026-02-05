"""
Example script for processing T1D vs Control perifusion data.

This script processes insulin (INS) and glucagon (GCG) secretion data from
Type 1 Diabetes (T1D) donors and non-diabetic (ND) controls, calculating
traits including basal secretion, AUCs, SIs, and IIs.

Data is read from Excel files and processed using the traits_for_all function
from peak_function.py, with results saved to CSV files.
"""

import pandas as pd
from peak_function import traits_for_all


# List of T1D donor identifiers
t1d_donor_names = [
    '20170110-AEAF406-T1D-23-0.4yM-AHN', '20170114-AEAJ194-T1D-23-5yM-HPAP-002-Islet perifusion data',
    '20170713-AEGI183-T1D-56-25yM-LOU-Islet perifusion data', '20171115-AEKL093-T1D-44-15yM-AHN-Islet perifusion data',
    '20180410-AFDE034-T1D-35-22yM-AHN-Islet perifusion data', '20181113-AFKG460-T1D-13-6yM-AHN-Islet perifusion data',
    '20181211-AFLC352-T1D-19-8yF-AHN-Islet perifusion data', '20190103-6480-T1D-17-2yM-nPOD-Islet perifusion data',
    '20190201-6485-T1D-10-8yM-nPOD-Islet perifusion data', '20190917-RRIDSAMN12748653-T1D-30yM-ALB-Islet perifusion data',
    '20191211-AGLF388-T1D-21-14yM-AHN-Islet perifusion data', '20200128-AHAW082-T1D-26y-12yM-AHN-Islet perifusion data',
    '20200201-AHA1087-T1D-24y-7yM-HPAP055-Islet perifusion data', '20180925-RRIDSAMN19776463-T1D-10y-F-HPAP',
    '20200716-RRIDSAMN19842593-T1D-24y-M-HPAP', '20230621-RRIDSAMN34280071-T1D-35y-F-HPAP',
    '20231103-RRIDSAMN36405517-T1D-31y-M-HPAP', '20231103-RRIDSAMN37875591-T1D-27y-M-HPAP'
]

########################
#        GCG IEQ       #
########################
t1d_gcg_ieq = pd.read_excel(
    '../data/T1D vs Ctrls.xlsx',
    sheet_name='T1D GCG IEQs_min',
    skiprows=1, nrows=51,  # only use the first 51 rows
    usecols=list(range(21))  # only use the first 21 columns
)
t1d_gcg_ieq.drop(['Fraction', 'Stimulus'], axis=1, inplace=True)
t1d_gcg_ieq.columns = ['time'] + t1d_donor_names

nd_gcg_ieq = pd.read_excel(
    '../data/T1D vs Ctrls.xlsx',
    sheet_name='ND Ctrls GCG IEQ',
    skiprows=2, nrows=50,
    usecols=list(range(7, 19)) + list(range(21, 35))
)

# Merge ND and T1D data
t1d_and_ctrl_gcg_ieq = pd.concat([t1d_gcg_ieq, nd_gcg_ieq], axis=1)

# Load parameters for INS IEQ analysis
param_df = pd.read_csv(
    '../parameter/GCG_IEQ_parameter.csv'
)

# Calculate traits for INS IEQ
res = traits_for_all(
    t1d_and_ctrl_gcg_ieq,
    param_df,
    trait_prefix='GCG-IEQ'
)
res.to_csv('../output/GCG_IEQ_traits.csv', index=False)

########################
#     INS content      #
########################
t1d_gcg_content = pd.read_excel(
    '../data/T1D vs Ctrls.xlsx',
    sheet_name='T1D GCG Content_min',
    skiprows=1, nrows=51,
    usecols=list(range(21))
)
t1d_gcg_content.drop(['Fraction', 'Stimulus'], axis=1, inplace=True)
t1d_gcg_content.columns = ['time'] + t1d_donor_names

nd_gcg_content = pd.read_excel(
    '../data/T1D vs Ctrls.xlsx',
    sheet_name='ND Ctrls GCG Cont.',
    skiprows=2, nrows=50,
    usecols=list(range(7, 19)) + list(range(19, 34))
)

# Merge ND and T1D data
t1d_and_ctrl_gcg_content = pd.concat([t1d_gcg_content, nd_gcg_content], axis=1)

# Load parameters for INS content analysis
param_df = pd.read_csv(
    '../parameter/GCG_content_parameter.csv'
)

# Calculate traits for INS content
res = traits_for_all(
    t1d_and_ctrl_gcg_content,
    param_df,
    trait_prefix='GCG-content'
)
res.to_csv('../output/GCG_content_traits.csv', index=False)

