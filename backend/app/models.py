from sqlalchemy import Boolean, Column, Integer, String, Float, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    workout_logs = relationship("WorkoutLog", back_populates="owner")
    inbody_records = relationship("Inbody", back_populates="owner")

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

    # User와의 외래 키 관계 설정
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="workout_logs")

# 인바디 데이터를 저장하는 테이블
class Inbody(Base):
    __tablename__ = "inbody_records"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    weight = Column(Float)
    muscle_mass = Column(Float)
    fat_percent = Column(Float)

    # User와의 외래 키 관계 설정
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="inbody_records")

    __table_args__ = (
        # 한 사용자는 특정 날짜에 하나의 인바디 기록만 가질 수 있도록 복합 고유 제약 조건 설정
        UniqueConstraint('owner_id', 'date', name='_owner_date_uc'),
    )
