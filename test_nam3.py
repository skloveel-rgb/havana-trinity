import pandas as pd
df_j = pd.read_excel('정시_전국.xlsx', sheet_name='Sheet1', header=2)
univs = df_j.iloc[:, 1].dropna().unique()
for u in univs:
    if '남' in str(u):
        print(u)
