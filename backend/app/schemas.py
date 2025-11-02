from pydantic import BaseModel, Field, computed_field
from datetime import date
from typing import List, Dict, Optional

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

    @computed_field
    @property
    def exercise_name(self) -> str:
        return self.exercise.name

    class Config:
        orm_mode = True
        from_attributes = True # Pydantic v2

class InbodyBase(BaseModel):
    date: date
    weight: float
    muscle_mass: float
    fat_percent: float

class InbodyCreate(InbodyBase):
    pass

class Inbody(InbodyBase):
    id: int

    class Config:
        orm_mode = True


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
    pushData: Dict[str, ChartData]
    pullData: Dict[str, ChartData]
    legData: Dict[str, ChartData]
    inbodyData: InbodyChartData

class CSVMigrationResult(BaseModel):
    exercises: int
    inbody_records: int
    workout_logs: int

class CSVMigrationResponse(BaseModel):
    message: str
    result: CSVMigrationResult

