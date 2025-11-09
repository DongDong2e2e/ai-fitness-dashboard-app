from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..services.chatbot_service import ChatbotService
from ..database import get_db
from ..dependencies import get_chatbot_service, get_current_active_user
from .. import models

router = APIRouter(
    prefix="/api/v1",
    tags=["chatbot"]
)

@router.post("/chat")
async def chat_with_bot(
    message: dict,
    db: Session = Depends(get_db),
    chatbot_service: ChatbotService = Depends(get_chatbot_service),
    current_user: models.User = Depends(get_current_active_user)
):
    user_message = message.get("message")
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        response = chatbot_service.process_user_message(user_message, db, current_user)
        return response
    except ValueError as e:
        # GEMINI_API_KEY가 설정되지 않았을 때 등 설정 관련 오류 처리
        raise HTTPException(status_code=500, detail=f"Chatbot configuration error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot processing failed: {e}")
