from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import crud, models, schemas
from .database import get_db
from .security import oauth2_scheme, decode_access_token
from .services.report_generator import ReportGeneratorService
from .services.dashboard_service import DashboardService
from .services.chatbot_service import ChatbotService

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_access_token(token)
    if token_data.email is None:
        raise credentials_exception
    user = crud.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_report_generator_service() -> ReportGeneratorService:
    return ReportGeneratorService()

def get_dashboard_service() -> DashboardService:
    return DashboardService()

def get_chatbot_service() -> ChatbotService:
    return ChatbotService()
