# -*- coding: utf-8 -*-
import sys
from data_engine import UNIV_GED_TABLES, engine

sys.stdout.reconfigure(encoding='utf-8')

print("=========================================================")
print("           대학별 검정고시 환산 등급표 전수 검증          ")
print("=========================================================")

processed = set()
for u_name, table in UNIV_GED_TABLES.items():
    t_tuple = tuple(table)
    if t_tuple in processed:
        continue
    processed.add(t_tuple)
    print(f"\n[대학 그룹: {u_name}]")
    print("  원점수 -> 환산등급 매핑:")
    for cutoff, grade in table:
        print(f"    - {cutoff}점 이상: {grade:.2f} 등급")

print("\n=========================================================")
print("           주요 대학 100점 / 98점 / 95점 / 90점 테스트   ")
print("=========================================================")
test_univs = ['충남대학교', '공주대학교', '가천대학교', '명지대학교', '경기대학교', '삼육대학교', '덕성여자대학교', '부산대학교']
for u in test_univs:
    scores_str = []
    for s in [100.0, 98.0, 95.0, 90.0]:
        g = engine.convert_ged_to_gpa(s, u, '')
        scores_str.append(f"{s}점: {g}등급")
    print(f"{u:12s} -> " + ", ".join(scores_str))
