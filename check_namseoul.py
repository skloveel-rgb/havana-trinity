import pandas as pd
import warnings
warnings.filterwarnings('ignore')

print('--- JUNGSI DATA ---')
try:
    df_j = pd.read_excel('정시_전국.xlsx', sheet_name='Sheet1', header=2)
    df_j = df_j[df_j.iloc[:, 1].astype(str).str.contains('남서울')]
    for _, row in df_j.head(10).iterrows():
        print(f'{row.iloc[5]} | 2024cut: {row.iloc[16]} | 2023cut: {row.iloc[15]} | eval: {row.iloc[9]}')
except Exception as e:
    print('Jungsi error:', e)

