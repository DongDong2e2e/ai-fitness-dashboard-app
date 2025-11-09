from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .. import crud, models, schemas
from ..database import get_db
from ..dependencies import get_current_active_user

router = APIRouter(
    prefix="/api/v1",
    tags=["inbody"]
)

@router.get("/inbody-records", response_model=List[schemas.Inbody])
def read_inbody_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Retrieve inbody records for the current user.
    """
    return crud.get_inbody_records_by_user(db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/inbody-records", response_model=schemas.Inbody)
def create_new_inbody_record(
    inbody: schemas.InbodyCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Create a new inbody record for the current user.
    """
    try:
        return crud.create_inbody_record(db=db, inbody=inbody, user_id=current_user.id)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An inbody record for this date already exists for the current user."
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, 
            detail=f"An unexpected error occurred: {e}"
        )
