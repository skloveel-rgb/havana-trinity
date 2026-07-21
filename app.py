import os
from fastapi import FastAPI, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from data_engine import engine

app = FastAPI(title="2026 하바나-트리니티 대입 엔진 API")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(STATIC_DIR, exist_ok=True)

@app.get("/api/summary")
def get_summary():
    susi_count = len(engine.df_susi) if engine.df_susi is not None else 0
    jungsi_count = len(engine.df_jungsi) if engine.df_jungsi is not None else 0
    
    susi_univs = len(engine.df_susi['대학'].unique()) if susi_count > 0 else 0
    jungsi_univs = len(engine.df_jungsi['대학'].unique()) if jungsi_count > 0 else 0
    
    regions = sorted(list(set(engine.df_susi['지역'].dropna().unique()))) if susi_count > 0 else []

    return {
        "engine_name": "2026 하바나-트리니티 대입 엔진",
        "susi_units": susi_count,
        "jungsi_units": jungsi_count,
        "susi_univ_count": susi_univs,
        "jungsi_univ_count": jungsi_univs,
        "regions": ["전체"] + [r for r in regions if r != "기타" and len(r) > 0]
    }

@app.get("/api/analyze/susi")
def analyze_susi(
    input_type: str = Query("gpa", description="gpa: 고교내신, ged: 검정고시"),
    score: float = Query(2.5, description="내신 등급 또는 검정고시 평균 원점수"),
    region: str = Query("전체"),
    univ: str = Query("전체"),
    category: str = Query("전체"),
    admission_type: str = Query("전체"),
    dept: str = Query(""),
    univ_type: str = Query("전체", description="전체, 국공립, 사립"),
    sort_by: str = Query("status", description="status: 소신->적정->안정, rank: 대학서열순"),
    limit: int = Query(50000)
):
    results = engine.diagnose_susi(
        input_type=input_type,
        score_val=score,
        region_filter=region,
        univ_filter=univ,
        category_filter=category,
        type_filter=admission_type,
        dept_filter=dept,
        univ_type_filter=univ_type,
        sort_by=sort_by
    )
    return {
        "status": "success",
        "engine": "2026 하바나-트리니티 대입 엔진",
        "input_type": input_type,
        "input_score": score,
        "total_matches": len(results),
        "results": results[:limit]
    }

@app.get("/api/analyze/jungsi")
def analyze_jungsi(
    percentile: float = Query(85.0, description="수능 백분위 평균"),
    region: str = Query("전체"),
    group: str = Query("전체"),
    sort_by: str = Query("status", description="status: 소신->적정->안정, rank: 대학서열순"),
    limit: int = Query(50000)
):
    results = engine.diagnose_jungsi(
        percentile_val=percentile,
        region_filter=region,
        group_filter=group,
        sort_by=sort_by
    )
    return {
        "status": "success",
        "engine": "2026 하바나-트리니티 대입 엔진",
        "input_percentile": percentile,
        "total_matches": len(results),
        "results": results[:limit]
    }

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/")
def read_root():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "2026 하바나-트리니티 대입 엔진 동작 중."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
