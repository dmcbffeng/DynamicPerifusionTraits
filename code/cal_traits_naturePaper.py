import pandas as pd
from peak_function import traits_for_all

### INS IEQ
ins_ieq = pd.read_excel(
    '../data/41586_2023_6693_MOESM8_ESM.xlsx', sheet_name='INS-IEQ',
    skiprows=3
)
ins_ieq.columns = ins_ieq.columns.astype(str)
for col in ins_ieq.columns:
    ins_ieq[col] = pd.to_numeric(ins_ieq[col], errors='coerce')
print(ins_ieq.columns)
param_df = pd.read_csv(
    '../parameter/INS_IEQ_parameter.csv'
)
# Calculate traits for INS IEQ
res1 = traits_for_all(
    ins_ieq,
    param_df,
    trait_prefix='INS-IEQ'
)

### INS content
ins_content = pd.read_excel(
    '../data/41586_2023_6693_MOESM8_ESM.xlsx', sheet_name='INS-content',
    skiprows=3
)
ins_content.columns = ins_content.columns.astype(str)
for col in ins_content.columns:
    ins_content[col] = pd.to_numeric(ins_content[col], errors='coerce')
print(ins_content.columns)
param_df = pd.read_csv(
    '../parameter/INS_content_parameter.csv'
)
# Calculate traits for INS IEQ
res2 = traits_for_all(
    ins_content,
    param_df,
    trait_prefix='INS-content'
)


### GCG IEQ
gcg_ieq = pd.read_excel(
    '../data/41586_2023_6693_MOESM8_ESM.xlsx', sheet_name='GCG-IEQ',
    skiprows=3
)
gcg_ieq.columns = gcg_ieq.columns.astype(str)
for col in gcg_ieq.columns:
    gcg_ieq[col] = pd.to_numeric(gcg_ieq[col], errors='coerce')
print(gcg_ieq.columns)
param_df = pd.read_csv(
    '../parameter/GCG_IEQ_parameter.csv'
)
# Calculate traits for INS IEQ
res3 = traits_for_all(
    gcg_ieq,
    param_df,
    trait_prefix='GCG-IEQ'
)

### INS content
gcg_content = pd.read_excel(
    '../data/41586_2023_6693_MOESM8_ESM.xlsx', sheet_name='GCG-content',
    skiprows=3
)
gcg_content.columns = gcg_content.columns.astype(str)
for col in gcg_content.columns:
    gcg_content[col] = pd.to_numeric(gcg_content[col], errors='coerce')
print(gcg_content.columns)
param_df = pd.read_csv(
    '../parameter/GCG_content_parameter.csv'
)
res4 = traits_for_all(
    gcg_content,
    param_df,
    trait_prefix='INS-content'
)

res1.set_index('Donor ID', inplace=True)
print(res1)
res2.set_index('Donor ID', inplace=True)
print(res2)
res3.set_index('Donor ID', inplace=True)
print(res3)
res4.set_index('Donor ID', inplace=True)
print(res4)
merged = pd.concat([res1, res2, res3, res4], axis=1)
merged.to_csv('../output/nature_all_traits.csv', index=True)


