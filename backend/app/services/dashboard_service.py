from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app import models

class DashboardService:
    def get_dashboard_data(self, db: Session, user_id: int) -> dict:
        """
        Retrieves and processes all data required for the main dashboard for a specific user.
        """
        three_months_ago = datetime.now().date() - timedelta(days=90)

        def format_date(date_obj):
            return date_obj.strftime('%Y-%m-%d')

        # 운동 데이터 조회
        def extract_workout_data(exercise_names: list):
            workout_data = {}
            for name in exercise_names:
                exercise = db.query(models.ExerciseInfo).filter(models.ExerciseInfo.name == name).first()
                if not exercise:
                    continue

                logs = db.query(models.WorkoutLog.date, models.WorkoutLog.weight)\
                    .filter(
                        models.WorkoutLog.exercise_id == exercise.id,
                        models.WorkoutLog.owner_id == user_id,
                        models.WorkoutLog.date >= three_months_ago
                    )\
                    .order_by(models.WorkoutLog.date).all()

                daily_max = {}
                for log in logs:
                    date_str = format_date(log.date)
                    if date_str not in daily_max or log.weight > daily_max[date_str]:
                        daily_max[date_str] = log.weight
                
                sorted_dates = sorted(daily_max.keys())
                if sorted_dates:
                    workout_data[name] = {"labels": sorted_dates, "data": [daily_max[date] for date in sorted_dates]}
            return workout_data

        def get_exercises_by_category(category_name: str) -> list[str]:
            return [exercise.name for exercise in db.query(models.ExerciseInfo).filter(models.ExerciseInfo.category == category_name).all()]

        push_exercises = get_exercises_by_category("Push")
        pull_exercises = get_exercises_by_category("Pull")
        leg_exercises = get_exercises_by_category("Leg")
        
        push_data = extract_workout_data(push_exercises)
        pull_data = extract_workout_data(pull_exercises)
        leg_data = extract_workout_data(leg_exercises)

        # 인바디 데이터 조회
        inbody_records = db.query(models.Inbody)\
            .filter(
                models.Inbody.owner_id == user_id,
                models.Inbody.date >= three_months_ago
            )\
            .order_by(models.Inbody.date).all()

        inbody_chart_data = {
            "labels": [format_date(rec.date) for rec in inbody_records],
            "weight": [rec.weight for rec in inbody_records],
            "muscle": [rec.muscle_mass for rec in inbody_records],
            "fatPercent": [rec.fat_percent * 100 for rec in inbody_records]
        }

        return {"pushData": push_data, "pullData": pull_data, "legData": leg_data, "inbodyData": inbody_chart_data}
