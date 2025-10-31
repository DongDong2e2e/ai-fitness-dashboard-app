import csv
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app import models

class DataImporterService:
    def __init__(self, db: Session):
        self.db = db
        self.exercise_map = {}

    def import_all_data(self, data_path: str):
        self.import_exercise_info(f"{data_path}/운동데이터_텍스트ver_구글 시트 - 운동분류.csv")
        self.import_inbody_records(f"{data_path}/운동데이터_텍스트ver_구글 시트 - Inbody_data.csv")
        self.import_workout_logs(f"{data_path}/운동데이터_텍스트ver_구글 시트 - structured_log.csv")
        
        # 간단한 결과 리포트 반환
        return {
            "exercises": self.db.query(models.ExerciseInfo).count(),
            "inbody_records": self.db.query(models.Inbody).count(),
            "workout_logs": self.db.query(models.WorkoutLog).count()
        }

    def import_exercise_info(self, file_path: str):
        print("Importing exercise info...")
        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    name = row['운동명'].strip()
                    if not name or name.startswith('**'):
                        continue
                    
                    db_exercise = self.db.query(models.ExerciseInfo).filter(models.ExerciseInfo.name == name).first()
                    if not db_exercise:
                        db_exercise = models.ExerciseInfo(
                            name=name,
                            category=row.get('대분류'),
                            calc_multiplier=float(row['볼륨계산']) if row.get('볼륨계산') else 1.0,
                            tool=row.get('도구'),
                            movement=row.get('움직임'),
                            target=row.get('주동근')
                        )
                        self.db.add(db_exercise)
                self.db.commit()
        except FileNotFoundError:
            print(f"Warning: Exercise info file not found at {file_path}")
            return
        # Create a map for faster lookups later
        self.exercise_map = {ex.name: ex.id for ex in self.db.query(models.ExerciseInfo).all()}
        print("Exercise info import complete.")

    def import_inbody_records(self, file_path: str):
        print("Importing InBody records...")
        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    try:
                        record_date = datetime.strptime(row['날짜'], '%Y-%m-%d').date()
                        existing_record = self.db.query(models.Inbody).filter(models.Inbody.date == record_date).first()
                        if not existing_record:
                            db_inbody = models.Inbody(
                                date=record_date,
                                weight=float(row['체중(kg)']),
                                muscle_mass=float(row['골격근량(kg)']),
                                fat_percent=float(row['체지방률(%)'].replace('%','')) / 100
                            )
                            self.db.add(db_inbody)
                    except (ValueError, KeyError) as e:
                        print(f"Skipping malformed InBody row: {row} -> {e}")
                        continue
                self.db.commit()
        except FileNotFoundError:
            print(f"Warning: InBody records file not found at {file_path}")
        print("InBody records import complete.")

    def import_workout_logs(self, file_path: str):
        print("Importing workout logs...")
        if not self.exercise_map:
            print("Exercise map is empty. Run import_exercise_info first.")
            return
        try:
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                logs_to_add = []
                for row in reader:
                    try:
                        exercise_name = row['운동명'].strip()
                        exercise_id = self.exercise_map.get(exercise_name)
                        if not exercise_id:
                            continue

                        log_date = datetime.strptime(row['날짜'], '%Y-%m-%d').date()
                        
                        # 더 빠른 처리를 위해 add만 하고 마지막에 commit
                        db_log = models.WorkoutLog(
                            date=log_date,
                            exercise_id=exercise_id,
                            set_type=row.get('세트_구분'),
                            set_num=row.get('세트번호'),
                            weight=float(row['무게(kg)'] or 0),
                            reps_or_time=float(row['횟수/시간'] or 0),
                            unit=row.get('단위'),
                            volume=float(row['볼륨(kg)'] or 0)
                        )
                        logs_to_add.append(db_log)
                    except (ValueError, KeyError) as e:
                        print(f"Skipping malformed workout log row: {row} -> {e}")
                        continue
                
                print(f"Adding {len(logs_to_add)} workout logs to session...")
                self.db.bulk_save_objects(logs_to_add)
                self.db.commit()
        except FileNotFoundError:
            print(f"Warning: Workout logs file not found at {file_path}")
        print("Workout logs import complete.")

