import csv
from datetime import datetime
from sqlalchemy.orm import Session
from app import models, schemas
from pydantic import ValidationError

class DataImporterService:
    def __init__(self, db: Session):
        self.db = db
        self.exercise_map = {}
        self.errors = []

    def import_all_data(self, data_path: str):
        self.import_exercise_info(f"{data_path}/운동데이터_텍스트ver_구글 시트 - 운동분류.csv")
        self.import_inbody_records(f"{data_path}/운동데이터_텍스트ver_구글 시트 - Inbody_data.csv")
        self.import_workout_logs(f"{data_path}/운동데이터_텍스트ver_구글 시트 - structured_log.csv")
        
        return {
            "exercises": self.db.query(models.ExerciseInfo).count(),
            "inbody_records": self.db.query(models.Inbody).count(),
            "workout_logs": self.db.query(models.WorkoutLog).count(),
            "errors": self.errors
        }

    def import_exercise_info(self, file_path: str):
        print("Importing exercise info...")
        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for i, row in enumerate(reader, 1):
                    try:
                        name = row['운동명'].strip()
                        if not name or name.startswith('**'):
                            continue
                        
                        validated_data = schemas.ExerciseInfoCreate(**row)

                        db_exercise = self.db.query(models.ExerciseInfo).filter(models.ExerciseInfo.name == validated_data.name).first()
                        if not db_exercise:
                            db_exercise = models.ExerciseInfo(**validated_data.dict())
                            self.db.add(db_exercise)
                    except (ValidationError, KeyError) as e:
                        self.errors.append(f"File: {file_path}, Row: {i+1}, Error: {e}")
                        continue
                self.db.commit()
        except FileNotFoundError:
            self.errors.append(f"File not found: {file_path}")
            return
        self.exercise_map = {ex.name: ex.id for ex in self.db.query(models.ExerciseInfo).all()}
        print("Exercise info import complete.")

    def import_inbody_records(self, file_path: str):
        print("Importing InBody records...")
        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for i, row in enumerate(reader, 1):
                    try:
                        record_date = datetime.strptime(row['날짜'], '%Y-%m-%d').date()
                        existing_record = self.db.query(models.Inbody).filter(models.Inbody.date == record_date).first()
                        if not existing_record:
                            validated_data = schemas.InbodyCreate(date=record_date, **row)
                            db_inbody = models.Inbody(**validated_data.dict())
                            self.db.add(db_inbody)
                    except (ValidationError, ValueError, KeyError) as e:
                        self.errors.append(f"File: {file_path}, Row: {i+1}, Error: {e}")
                        continue
                self.db.commit()
        except FileNotFoundError:
            self.errors.append(f"File not found: {file_path}")
        print("InBody records import complete.")

    def import_workout_logs(self, file_path: str):
        print("Importing workout logs...")
        if not self.exercise_map:
            self.errors.append("Exercise map is empty. Run import_exercise_info first.")
            return
        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                logs_to_add = []
                for i, row in enumerate(reader, 1):
                    try:
                        exercise_name = row['운동명'].strip()
                        exercise_id = self.exercise_map.get(exercise_name)
                        if not exercise_id:
                            self.errors.append(f"File: {file_path}, Row: {i+1}, Error: Exercise '{exercise_name}' not found in exercise map.")
                            continue

                        log_date = datetime.strptime(row['날짜'], '%Y-%m-%d').date()
                        validated_data = schemas.WorkoutLogCreate(date=log_date, exercise_name=exercise_name, **row)
                        
                        db_log = models.WorkoutLog(
                            date=validated_data.date,
                            exercise_id=exercise_id,
                            set_type=validated_data.set_type,
                            set_num=validated_data.set_num,
                            weight=validated_data.weight,
                            reps_or_time=validated_data.reps_or_time,
                            unit=validated_data.unit,
                            volume=float(row.get('볼륨(kg)', 0) or 0)
                        )
                        logs_to_add.append(db_log)
                    except (ValidationError, ValueError, KeyError) as e:
                        self.errors.append(f"File: {file_path}, Row: {i+1}, Error: {e}")
                        continue
                
                print(f"Adding {len(logs_to_add)} workout logs to session...")
                self.db.bulk_save_objects(logs_to_add)
                self.db.commit()
        except FileNotFoundError:
            self.errors.append(f"File not found: {file_path}")
        print("Workout logs import complete.")

