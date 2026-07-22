import pandas as pd
df_s = pd.read_excel('2026 IDA입시연구소 수시배치표 ver.10 통합엑셀.xlsx', sheet_name='전체 대학', header=3)
univs = df_s.iloc[:, 2].dropna().unique()
with open('univs_susi.txt', 'w', encoding='utf-8') as f:
    for u in univs:
        if '남서울' in str(u):
            f.write(str(u) + '\n')
            for _, row in df_s[df_s.iloc[:, 2] == u].iterrows():
                dept = str(row.iloc[6])
                if '시각' in dept:
                    f.write(f"  {dept} | 25컷:{row.iloc[42]} | 24컷:{row.iloc[40]}\n")
