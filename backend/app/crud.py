from sqlalchemy.orm import Session
from . import models, schemas

def get_exercise_by_name(db: Session, name: str):
    return db.query(models.ExerciseInfo).filter(models.ExerciseInfo.name == name).first()

def create_exercise(db: Session, exercise: schemas.ExerciseInfoCreate) -> models.ExerciseInfo:
    db_exercise = models.ExerciseInfo(**exercise.dict())
    db.add(db_exercise)
    db.commit()
    db.refresh(db_exercise)
    return db_exercise

def create_workout_log(db: Session, log: schemas.WorkoutLogCreate) -> models.WorkoutLog:
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
        volume=volume
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def create_inbody_record(db: Session, inbody: schemas.InbodyCreate) -> models.Inbody:
    db_inbody = models.Inbody(**inbody.dict())
    db.add(db_inbody)
    db.commit()
    db.refresh(db_inbody)
    return db_inbody
