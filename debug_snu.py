# -*- coding: utf-8 -*-
import sys
from data_engine import engine

sys.stdout.reconfigure(encoding='utf-8')

res = engine.diagnose_susi(input_type='ged', score_val=96.0)
snu_yonsei = [r for r in res if '서울대' in r['univ'] or '연세대' in r['univ']]
print(f"Count of SNU / Yonsei results for 96.0: {len(snu_yonsei)}")
for r in snu_yonsei:
    print(f"Univ: {r['univ']} | Type: {r['type']} | SubType: {r['sub_type']} | Dept: {r['department']} | UserGrade: {r['user_grade']} | Cut3yr: {r['cutoff_3yr']}")
