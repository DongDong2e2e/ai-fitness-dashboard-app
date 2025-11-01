from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import crud, models, schemas
from ..database import get_db
from ..exceptions import DuplicateRecordError

router = APIRouter()

@router.post("/inbody-records", response_model=schemas.Inbody)
def create_new_inbody_record(inbody: schemas.InbodyCreate, db: Session = Depends(get_db)):
    # 날짜 중복 체크
    existing_record = db.query(models.Inbody).filter(models.Inbody.date == inbody.date).first()
    if existing_record:
        raise DuplicateRecordError(detail="A record for this date already exists.")
    try:
        return crud.create_inbody_record(db=db, inbody=inbody)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create InBody record: {e}")
