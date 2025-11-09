from sqlalchemy.orm import Session
from . import models, schemas
from .security import get_password_hash

# --- User CRUD ---
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- Exercise CRUD ---
def get_exercise_by_name(db: Session, name: str):
    return db.query(models.ExerciseInfo).filter(models.ExerciseInfo.name == name).first()

def create_exercise(db: Session, exercise: schemas.ExerciseInfoCreate) -> models.ExerciseInfo:
    db_exercise = models.ExerciseInfo(**exercise.dict())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

# --- WorkoutLog CRUD ---
def create_workout_log(db: Session, log: schemas.WorkoutLogCreate, user_id: int) -> models.WorkoutLog:
    exercise = get_exercise_by_name(db, log.exercise_name)
    if not exercise:
        raise ValueError(f"Exercise '{log.exercise_name}' not found. Please add it first.")

    # 볼륨 계산
    volume = 0.0
    if log.unit == '회':
        volume = log.weight * log.reps_or_time * exercise.calc_multiplier

    db_log = models.WorkoutLog(
        date=log.date,
        exercise_id=exercise.id,
        set_type=log.set_type,
        set_num=log.set_num,
        weight=log.weight,
        reps_or_time=log.reps_or_time,
        unit=log.unit,
        volume=volume,
        owner_id=user_id
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    # Eagerly load the exercise relationship for the response model
    db_log.exercise = exercise
    return db_log

def get_workout_logs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.WorkoutLog).filter(models.WorkoutLog.owner_id == user_id).order_by(models.WorkoutLog.date.desc()).offset(skip).limit(limit).all()

# --- Inbody CRUD ---
def create_inbody_record(db: Session, inbody: schemas.InbodyCreate, user_id: int) -> models.Inbody:
    db_inbody = models.Inbody(**inbody.dict(), owner_id=user_id)
    db.add(db_inbody)
    db.commit()
    db.refresh(db_inbody)
    return db_inbody

def get_inbody_records_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Inbody).filter(models.Inbody.owner_id == user_id).order_by(models.Inbody.date.desc()).offset(skip).limit(limit).all()
