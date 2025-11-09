from fastapi import FastAPI, HTTPException, Depends, Request
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import create_engine
import os

from . import models, schemas
from .database import Base, get_db
from .config import settings
from .services.report_generator import ReportGeneratorService
from .services.data_importer import DataImporterService
from .services.dashboard_service import DashboardService
from .routers import workouts, inbody, chatbot, exercises, auth
from .dependencies import get_dashboard_service, get_report_generator_service, get_current_active_user
from .exceptions import DuplicateRecordError, duplicate_record_exception_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    if os.getenv("TESTING") != "True":
        # Create engine and session factory
        SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"
        app.state.engine = create_engine(SQLALCHEMY_DATABASE_URL)
        app.state.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=app.state.engine)

        # Create tables
        # Base.metadata.create_all(bind=app.state.engine) # Replaced by Alembic
    yield

# FastAPI app creation
app = FastAPI(lifespan=lifespan)

# Middleware for creating a new DB session for each request
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = None
    try:
        if os.getenv("TESTING") == "True":
            # For testing, db session is handled by pytest fixtures
            response = await call_next(request)
        else:
            session = app.state.SessionLocal()
            request.state.db = session
            response = await call_next(request)
    finally:
        if response and os.getenv("TESTING") != "True":
            request.state.db.close()
    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
app.add_exception_handler(DuplicateRecordError, duplicate_record_exception_handler)

# Routers
app.include_router(auth.router)
app.include_router(workouts.router, prefix="/api/v1", tags=["workouts"])
app.include_router(inbody.router, prefix="/api/v1", tags=["inbody"])
app.include_router(chatbot.router, prefix="/api/v1", tags=["chatbot"])
app.include_router(exercises.router, prefix="/api/v1", tags=["exercises"])

@app.get("/")
def read_root():
    return {"Hello": "Backend World with PostgreSQL"}

@app.post("/api/v1/migrate-data-from-csv", response_model=schemas.CSVMigrationResponse)
def migrate_data_from_csv(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_active_user)):
    """
    (User-specific)
    Migrates data from local CSV files to the database for the current user.
    """
    try:
        importer = DataImporterService(db)
        # app/data 폴더를 기준으로 경로 설정
        data_path = os.path.join(os.path.dirname(__file__), 'data')
        result = importer.import_all_data(data_path, user_id=current_user.id)
        return {"message": "Data migration from CSV completed successfully.", "result": result}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=f"Data file not found: {e}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Data processing error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during data migration: {e}")


@app.get("/api/v1/dashboard-data", response_model=schemas.DashboardData)
def get_dashboard_data(
    db: Session = Depends(get_db),
    dashboard_service: DashboardService = Depends(get_dashboard_service),
    current_user: models.User = Depends(get_current_active_user)
):
    try:
        return dashboard_service.get_dashboard_data(db, user_id=current_user.id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard data: {e}")

# --- 리포트 엔드포인트 ---
@app.post("/api/v1/send-report/{report_type}")
async def send_report(
    report_type: str,
    db: Session = Depends(get_db),
    report_generator_service: ReportGeneratorService = Depends(get_report_generator_service),
    current_user: models.User = Depends(get_current_active_user)
):
    if report_type not in ["week", "month", "quarter", "year"]:
        raise HTTPException(status_code=400, detail="Invalid report type.")
    try:
        report_generator_service.send_report(report_type, db, current_user=current_user)
        return {"message": f"{report_type.capitalize()} report sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send report: {e}")
