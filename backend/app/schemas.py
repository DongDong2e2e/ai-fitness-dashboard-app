from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import List, Optional

# --- Token Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# --- User Schemas ---
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool
    workout_logs: List['WorkoutLog'] = []
    inbody_records: List['Inbody'] = []

    class Config:
        orm_mode = True
        from_attributes = True

# --- Base Models for DB records ---
class ExerciseInfoBase(BaseModel):
    name: str
    category: Optional[str] = None
    calc_multiplier: Optional[float] = 1.0

class ExerciseInfoCreate(ExerciseInfoBase):
    pass

class ExerciseInfo(ExerciseInfoBase):
    id: int
    class Config:
        orm_mode = True

class WorkoutLogBase(BaseModel):
    date: date
    set_type: str
    set_num: str
    weight: float
    reps_or_time: float
    unit: str

class WorkoutLogCreate(WorkoutLogBase):
    exercise_name: str

class WorkoutLog(WorkoutLogBase):
    id: int
    volume: float
    exercise: ExerciseInfo
    owner_id: int

    class Config:
        orm_mode = True
        from_attributes = True

class InbodyBase(BaseModel):
    date: date
    weight: float
    muscle_mass: float
    fat_percent: float

class InbodyCreate(InbodyBase):
    pass

class Inbody(InbodyBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True
        from_attributes = True

# Update forward references
User.model_rebuild()

# --- API Response Models ---

class ChartData(BaseModel):
    labels: List[str]
    data: List[float]

class InbodyChartData(BaseModel):
    labels: List[str]
    weight: List[float]
    muscle: List[float]
    fatPercent: List[float]

class DashboardData(BaseModel):
    pushData: dict[str, ChartData]
    pullData: dict[str, ChartData]
    legData: dict[str, ChartData]
    inbodyData: InbodyChartData

class CSVMigrationResult(BaseModel):
    exercises: int
    inbody_records: int
    workout_logs: int

class CSVMigrationResponse(BaseModel):
    message: str
    result: CSVMigrationResult

