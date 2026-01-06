import pandas as pd
from peak_function import traits_for_all



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

