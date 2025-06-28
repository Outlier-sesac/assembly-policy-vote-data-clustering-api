from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from clustering import run_clustering_from_db  # ← clustering.py 내부 함수 가져옴

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 배포 시 프론트 주소로 제한
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/api/clusters")
def get_clusters():
    try:
        data = run_clustering_from_db()  # SQL Server에서 데이터 조회 + 클러스터링
        return {"status": "success", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
