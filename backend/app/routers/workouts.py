from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter()

@router.post("/workout-logs", response_model=schemas.WorkoutLog)
def create_new_workout_log(log: schemas.WorkoutLogCreate, request: Request, db: Session = Depends(get_db)):
    try:
        return crud.create_workout_log(db=db, log=log)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create workout log: {e}")
