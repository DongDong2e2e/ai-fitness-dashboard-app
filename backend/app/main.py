from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import os

from . import models, schemas, crud
from .database import engine, get_db
from .services.report_generator import ReportGeneratorService
from .services.chatbot_service import ChatbotService
from .services.data_importer import DataImporterService
from .services.dashboard_service import DashboardService

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

# 서비스 초기화
report_generator_service = ReportGeneratorService()
chatbot_service = ChatbotService()
dashboard_service = DashboardService()

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
def get_dashboard_data(db: Session = Depends(get_db)):
    try:
        return dashboard_service.get_dashboard_data(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard data: {e}")

# --- 데이터 생성 엔드포인트 ---
@app.post("/api/workout-logs", response_model=schemas.WorkoutLog)
def create_new_workout_log(log: schemas.WorkoutLogCreate, db: Session = Depends(get_db)):
    try:
        return crud.create_workout_log(db=db, log=log)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workout log: {e}")

@app.post("/api/inbody-records", response_model=schemas.Inbody)
def create_new_inbody_record(inbody: schemas.InbodyCreate, db: Session = Depends(get_db)):
    # 날짜 중복 체크
    existing_record = db.query(models.Inbody).filter(models.Inbody.date == inbody.date).first()
    if existing_record:
        raise HTTPException(status_code=409, detail="A record for this date already exists.")
    try:
        return crud.create_inbody_record(db=db, inbody=inbody)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create InBody record: {e}")

# --- 리포트 및 챗봇 엔드포인트 ---
@app.post("/send-report/{report_type}")
async def send_report(report_type: str, db: Session = Depends(get_db)):
    if report_type not in ["week", "month", "quarter", "year"]:
        raise HTTPException(status_code=400, detail="Invalid report type.")
    try:
        report_generator_service.send_report(report_type, db)
        return {"message": f"{report_type.capitalize()} report sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send report: {e}")

@app.post("/chat")
async def chat_with_bot(message: dict, db: Session = Depends(get_db)):
    user_message = message.get("message")
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        response = chatbot_service.process_user_message(user_message, db)
        return response
    except ValueError as e:
        # GEMINI_API_KEY가 설정되지 않았을 때 등 설정 관련 오류 처리
        raise HTTPException(status_code=500, detail=f"Chatbot configuration error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot processing failed: {e}")
