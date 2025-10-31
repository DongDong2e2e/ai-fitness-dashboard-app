from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from backend.app import models
from backend.app.config import Config

class ReportAnalyzer:
    def analyze_data_for_period(self, db: Session, period_type: str):
        today = datetime.now().date()
        
        start_date, end_date, prev_start_date, prev_end_date, period_name, weeks_in_period = self._get_date_ranges(today, period_type)

        def extract_stats_for_period(start_dt, end_dt):
            if not start_dt or not end_dt:
                return {'totalWorkoutDays': 0, 'totalVolume': 0, 'mainFocusBodyPart': '없음', 'topExercises': [], 'bestPerformance': {'exercise': '없음', 'weight': 0, 'reps': 0}}

            base_query = db.query(models.WorkoutLog).filter(models.WorkoutLog.date.between(start_dt, end_dt))
            period_data = base_query.all()
            if not period_data:
                return {'totalWorkoutDays': 0, 'totalVolume': 0, 'mainFocusBodyPart': '없음', 'topExercises': [], 'bestPerformance': {'exercise': '없음', 'weight': 0, 'reps': 0}}

            total_workout_days = db.query(func.count(distinct(models.WorkoutLog.date))).filter(models.WorkoutLog.date.between(start_dt, end_dt)).scalar()
            total_volume = db.query(func.sum(models.WorkoutLog.volume)).filter(models.WorkoutLog.date.between(start_dt, end_dt)).scalar() or 0

            category_vol = db.query(models.ExerciseInfo.category, func.sum(models.WorkoutLog.volume).label('vol'))\
                .join(models.WorkoutLog, models.ExerciseInfo.id == models.WorkoutLog.exercise_id)\
                .filter(models.WorkoutLog.date.between(start_dt, end_dt))\
                .group_by(models.ExerciseInfo.category).order_by(func.sum(models.WorkoutLog.volume).desc()).first()
            main_focus_body_part = category_vol[0] if category_vol else '없음'

            top_exercises_query = db.query(models.ExerciseInfo.name, func.sum(models.WorkoutLog.volume).label('vol'))\
                .join(models.WorkoutLog, models.ExerciseInfo.id == models.WorkoutLog.exercise_id)\
                .filter(models.WorkoutLog.date.between(start_dt, end_dt))\
                .group_by(models.ExerciseInfo.name).order_by(func.sum(models.WorkoutLog.volume).desc()).limit(5).all()
            top_exercises_formatted = [{'exercise': name, 'volume': f'{volume:.0f}kg'} for name, volume in top_exercises_query]

            best_perf_log = db.query(models.WorkoutLog).join(models.ExerciseInfo)\
                .filter(models.WorkoutLog.date.between(start_dt, end_dt))\
                .order_by(models.WorkoutLog.weight.desc()).first()
            period_best = {'exercise': '없음', 'weight': 0.0, 'reps': 0.0}
            if best_perf_log:
                period_best = {'exercise': best_perf_log.exercise.name, 'weight': best_perf_log.weight, 'reps': best_perf_log.reps_or_time}

            return {
                'totalWorkoutDays': total_workout_days,
                'totalVolume': f'{total_volume:.0f}',
                'mainFocusBodyPart': main_focus_body_part,
                'topExercises': top_exercises_formatted,
                'bestPerformance': period_best
            }

        current_stats = extract_stats_for_period(start_date, end_date)
        previous_stats = extract_stats_for_period(prev_start_date, prev_end_date)

        avg_workout_days_per_week = round(current_stats['totalWorkoutDays'] / weeks_in_period) if weeks_in_period > 0 and current_stats['totalWorkoutDays'] > 0 else 0

        pr = {'exercise': '없음', 'record': ''}
        if current_stats['bestPerformance']['weight'] > 0:
            best_exercise_name = current_stats['bestPerformance']['exercise']
            best_exercise = db.query(models.ExerciseInfo).filter(models.ExerciseInfo.name == best_exercise_name).first()
            if best_exercise:
                previous_best_weight = db.query(func.max(models.WorkoutLog.weight))\
                    .filter(models.WorkoutLog.exercise_id == best_exercise.id, models.WorkoutLog.date < start_date).scalar() or 0
                
                if current_stats['bestPerformance']['weight'] > previous_best_weight:
                    pr['exercise'] = best_exercise_name
                    pr['record'] = f"{current_stats['bestPerformance']['weight']:.1f}kg x {current_stats['bestPerformance']['reps']:.0f}회"

        start_inbody = db.query(models.Inbody).filter(models.Inbody.date < start_date).order_by(models.Inbody.date.desc()).first()
        end_inbody = db.query(models.Inbody).filter(models.Inbody.date <= end_date).order_by(models.Inbody.date.desc()).first()
        if not end_inbody: end_inbody = start_inbody

        end_weight_str, end_muscle_str, end_fat_str = 'N/A', 'N/A', 'N/A'
        if end_inbody:
            start_w, start_m, start_f = (start_inbody.weight, start_inbody.muscle_mass, start_inbody.fat_percent) if start_inbody else (end_inbody.weight, end_inbody.muscle_mass, end_inbody.fat_percent)
            end_weight_str = f"{end_inbody.weight} kg{self._get_change_str(end_inbody.weight, start_w)}"
            end_muscle_str = f"{end_inbody.muscle_mass} kg{self._get_change_str(end_inbody.muscle_mass, start_m)}"
            end_fat_str = f"{end_inbody.fat_percent * 100:.1f}%{self._get_change_str(end_inbody.fat_percent, start_f)}"

        return {
            'userName': Config.USER_NAME,
            'periodName': period_name,
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'current': current_stats,
            'previous': previous_stats,
            'avgWorkoutDaysPerWeek': avg_workout_days_per_week,
            'prExercise': pr['exercise'],
            'prRecord': pr['record'],
            'endWeight': end_weight_str,
            'endMuscleMass': end_muscle_str,
            'endBodyFatPercent': end_fat_str
        }

    def _get_date_ranges(self, today, period_type):
        if period_type == 'week':
            end_date = today - timedelta(days=today.weekday() + 1)
            start_date = end_date - timedelta(days=6)
            weeks = 1
            name = f'{start_date.year}년 {start_date.isocalendar()[1]}주차'
        elif period_type == 'month':
            end_date = today.replace(day=1) - timedelta(days=1)
            start_date = end_date.replace(day=1)
            weeks = 4.345
            name = f'{start_date.year}년 {start_date.month}월'
        elif period_type == 'quarter':
            current_quarter = (today.month - 1) // 3
            end_date = datetime(today.year, current_quarter * 3 + 1, 1).date() - timedelta(days=1)
            start_date = datetime(end_date.year, (end_date.month - 1) // 3 * 3 + 1, 1).date()
            weeks = 13
            name = f'{start_date.year}년 {(start_date.month - 1) // 3 + 1}분기'
        elif period_type == 'year':
            last_year = today.year - 1
            end_date = datetime(last_year, 12, 31).date()
            start_date = datetime(last_year, 1, 1).date()
            weeks = 52
            name = f'{last_year}년'
        else:
            raise ValueError("Invalid period type")
        
        prev_end_date = start_date - timedelta(days=1)
        prev_start_date = prev_end_date - (end_date - start_date)
        
        return start_date, end_date, prev_start_date, prev_end_date, name, weeks

    def _get_change_str(self, current, previous):
        try:
            diff = float(current) - float(previous)
            if diff > 0: return f' (+{diff:.2f} ▲)'
            if diff < 0: return f' ({diff:.2f} ▼)'
            return ' (변화 없음)'
        except (ValueError, TypeError):
            return ''
