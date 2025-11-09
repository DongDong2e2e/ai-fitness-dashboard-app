from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..dependencies import get_current_active_user

router = APIRouter(
    prefix="/api/v1",
    tags=["workouts"]
)

@router.get("/workout-logs", response_model=List[schemas.WorkoutLog])
def read_workout_logs(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Retrieve workout logs for the current user.
    """
    return crud.get_workout_logs_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/workout-logs", response_model=schemas.WorkoutLog)
def create_new_workout_log(
    log: schemas.WorkoutLogCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new workout log for the current user.
    """
    try:
        return crud.create_workout_log(db=db, log=log, user_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workout log: {e}")
