import pandas as pd

df_j = pd.read_excel('정시_전국.xlsx', sheet_name='Sheet1', header=2)
df_j = df_j[df_j.iloc[:, 1].astype(str).str.contains('남서울')]
for _, row in df_j.iterrows():
    dept = str(row.iloc[5])
    print(f"DEPT: {dept} | 2024cut: {row.iloc[16]} | 2023cut: {row.iloc[15]} | Eval: {row.iloc[9]}")
