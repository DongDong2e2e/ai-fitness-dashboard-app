from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from . import models, schemas
from .database import engine, get_db
from .services.report_generator import ReportGeneratorService
from .services.data_importer import DataImporterService
from .services.dashboard_service import DashboardService
from .routers import workouts, inbody, chatbot
from .dependencies import get_dashboard_service, get_report_generator_service

# 데이터베이스 테이블 생성
models.Base.metadata.create_all(bind=engine)

# FastAPI 앱 생성
app = FastAPI()

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 포함
app.include_router(workouts.router, tags=["workouts"])
app.include_router(inbody.router, tags=["inbody"])
app.include_router(chatbot.router, tags=["chatbot"])

@app.get("/")
def read_root():
    return {"Hello": "Backend World with PostgreSQL"}

@app.post("/api/migrate-data-from-csv", response_model=schemas.CSVMigrationResponse)
def migrate_data_from_csv(db: Session = Depends(get_db)):
    """로컬 CSV 파일에서 데이터를 읽어와 PostgreSQL 데이터베이스에 저장합니다."""
    try:
        importer = DataImporterService(db)
        # app/data 폴더를 기준으로 경로 설정
        data_path = os.path.join(os.path.dirname(__file__), 'data')
        result = importer.import_all_data(data_path)
        return {"message": "Data migration from CSV completed successfully.", "result": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Data file not found: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Data processing error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during data migration: {e}")


@app.get("/api/dashboard-data", response_model=schemas.DashboardData)
def get_dashboard_data(db: Session = Depends(get_db), dashboard_service: DashboardService = Depends(get_dashboard_service)):
    try:
        return dashboard_service.get_dashboard_data(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard data: {e}")

# --- 리포트 엔드포인트 ---
@app.post("/send-report/{report_type}")
async def send_report(report_type: str, db: Session = Depends(get_db), report_generator_service: ReportGeneratorService = Depends(get_report_generator_service)):
    if report_type not in ["week", "month", "quarter", "year"]:
        raise HTTPException(status_code=400, detail="Invalid report type.")
    try:
        report_generator_service.send_report(report_type, db)
        return {"message": f"{report_type.capitalize()} report sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send report: {e}")
