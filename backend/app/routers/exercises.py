from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter()

@router.post("/exercises", response_model=schemas.ExerciseInfo)
def create_exercise(exercise: schemas.ExerciseInfoCreate, db: Session = Depends(get_db)):
    db_exercise = crud.get_exercise_by_name(db, name=exercise.name)
    if db_exercise:
        raise HTTPException(status_code=400, detail="Exercise already registered.")
    return crud.create_exercise(db=db, exercise=exercise)
