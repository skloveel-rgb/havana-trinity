import pandas as pd
df_j = pd.read_excel('정시_전국.xlsx', sheet_name='Sheet1', header=2)
univs = df_j.iloc[:, 1].dropna().unique()
with open('univs.txt', 'w', encoding='utf-8') as f:
    for u in univs:
        if '남서울' in str(u):
            f.write(str(u) + '\n')
            for _, row in df_j[df_j.iloc[:, 1] == u].iterrows():
                f.write(f"  {row.iloc[5]} | {row.iloc[16]} | {row.iloc[15]} | {row.iloc[9]}\n")
