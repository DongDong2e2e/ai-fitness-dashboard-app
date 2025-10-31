from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

# 운동 정보를 저장하는 테이블
class ExerciseInfo(Base):
    __tablename__ = "exercise_info"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=True)
    calc_multiplier = Column(Float, default=1.0)
    tool = Column(String, nullable=True)
    movement = Column(String, nullable=True)
    target = Column(String, nullable=True)

    # WorkoutLog와의 관계 설정
    logs = relationship("WorkoutLog", back_populates="exercise")

# 실제 운동 기록을 저장하는 테이블
class WorkoutLog(Base):
    __tablename__ = "workout_logs"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    set_type = Column(String)
    set_num = Column(String) # 'Warm-up' 같은 문자열이 들어갈 수 있으므로 String
    weight = Column(Float)
    reps_or_time = Column(Float)
    unit = Column(String)
    volume = Column(Float)

    # ExerciseInfo와의 외래 키 관계 설정
    exercise_id = Column(Integer, ForeignKey("exercise_info.id"))
    exercise = relationship("ExerciseInfo", back_populates="logs")

# 인바디 데이터를 저장하는 테이블
class Inbody(Base):
    __tablename__ = "inbody_records"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    weight = Column(Float)
    muscle_mass = Column(Float)
    fat_percent = Column(Float)
