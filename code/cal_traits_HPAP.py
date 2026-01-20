import pandas as pd
from peak_function import traits_for_all


df = pd.read_excel(
    '../data/HIPP_Report.xlsx', sheet_name='Insulin Results',
    skiprows=4, header=[0, 1]
)
# print(df)
ins_ieq, ins_content = {}, {}
for col in df.columns:
    if 'time' in col[0].lower():
        ins_ieq['time'] = df[col]
        ins_content['time'] = df[col]
    elif col[1] == 'ng/100 IEQ/min':
        ins_ieq[col[0]] = pd.to_numeric(df[col], errors='coerce')
    elif col[1] == '% content/min':
        ins_content[col[0]] = pd.to_numeric(df[col], errors='coerce')
ins_ieq = pd.DataFrame(ins_ieq)
ins_content = pd.DataFrame(ins_content)
# print(ins_ieq)
# print(ins_content)
param_df = pd.read_csv(
    '../parameter/INS_IEQ_parameter.csv'
)
# Calculate traits for INS IEQ
res1 = traits_for_all(
    ins_ieq,
    param_df,
    trait_prefix='INS-IEQ'
)
param_df = pd.read_csv(
    '../parameter/INS_content_parameter.csv'
)
# Calculate traits for INS IEQ
res2 = traits_for_all(
    ins_content,
    param_df,
    trait_prefix='INS-content'
)


df = pd.read_excel(
    '../data/HIPP_Report.xlsx', sheet_name='Glucagon Results',
    skiprows=4, header=[0, 1]
)
# print(df)
gcg_ieq, gcg_content = {}, {}
for col in df.columns:
    if 'time' in col[0].lower():
        gcg_ieq['time'] = df[col]
        gcg_content['time'] = df[col]
    elif col[1] == 'pg/100 IEQ/min':
        gcg_ieq[col[0]] = pd.to_numeric(df[col], errors='coerce')
    elif col[1] == '% content/min':
        gcg_content[col[0]] = pd.to_numeric(df[col], errors='coerce')
gcg_ieq = pd.DataFrame(ins_ieq)
gcg_content = pd.DataFrame(ins_content)

param_df = pd.read_csv(
    '../parameter/GCG_IEQ_parameter.csv'
)
# Calculate traits for INS IEQ
res3 = traits_for_all(
    gcg_ieq,
    param_df,
    trait_prefix='GCG-IEQ'
)
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


hpap_info = pd.read_excel('../data/Donor_Summary_197.xlsx', sheet_name='donor')
rr2hpap = {}
for i, row in hpap_info.iterrows():
    rr2hpap[row['rrid']] = row['donor_ID']
new_vec = []
for idx, row in merged.iterrows():
    if idx in rr2hpap:
        new_vec.append(rr2hpap[idx])
    else:
        new_vec.append(pd.NA)
merged['HPAP ID'] = new_vec
cols = list(merged.columns)
cols = [cols[-1]] + cols[:-1]
merged = merged[cols]
merged.to_csv('../output/HPAP_all_traits.csv', index=True)

