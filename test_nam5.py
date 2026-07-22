import pandas as pd
df_j = pd.read_excel('정시_전국.xlsx', sheet_name='Sheet1', header=2)
univs = df_j.iloc[:, 1].dropna().unique()
with open('all_univs.txt', 'w', encoding='utf-8') as f:
    for u in univs:
        f.write(str(u) + '\n')
