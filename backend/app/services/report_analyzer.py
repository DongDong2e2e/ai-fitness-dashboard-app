from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct

from backend.app import models
from backend.app.config import settings

# Constants
NO_DATA = "없음"
NO_CHANGE = " (변화 없음)"
UP_ARROW = " ▲"
DOWN_ARROW = " ▼"

class ReportAnalyzer:
    def analyze_data_for_period(self, db: Session, period_type: str):
        today = datetime.now().date()
        start_date, end_date, prev_start_date, prev_end_date, period_name, weeks_in_period = self._get_date_ranges(today, period_type)

        current_stats = self._extract_stats_for_period(db, start_date, end_date)
        previous_stats = self._extract_stats_for_period(db, prev_start_date, prev_end_date)

        avg_workout_days_per_week = self._calculate_avg_workout_days(current_stats, weeks_in_period)
        pr = self._calculate_pr(db, current_stats, start_date)
        inbody_changes = self._calculate_inbody_changes(db, start_date, end_date)

        return {
            'userName': settings.USER_NAME,
            'periodName': period_name,
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'current': current_stats,
            'previous': previous_stats,
            'avgWorkoutDaysPerWeek': avg_workout_days_per_week,
            'prExercise': pr['exercise'],
            'prRecord': pr['record'],
            **inbody_changes
        }

    def _extract_stats_for_period(self, db: Session, start_dt, end_dt):
        if not start_dt or not end_dt:
            return self._empty_stats()

        base_query = db.query(models.WorkoutLog).filter(models.WorkoutLog.date.between(start_dt, end_dt))
        if not base_query.first():
            return self._empty_stats()

        total_workout_days = db.query(func.count(distinct(models.WorkoutLog.date))).filter(models.WorkoutLog.date.between(start_dt, end_dt)).scalar()
        total_volume = db.query(func.sum(models.WorkoutLog.volume)).filter(models.WorkoutLog.date.between(start_dt, end_dt)).scalar() or 0

        main_focus_body_part = self._get_main_focus(db, start_dt, end_dt)
        top_exercises = self._get_top_exercises(db, start_dt, end_dt)
        period_best = self._get_best_performance(db, start_dt, end_dt)

        return {
            'totalWorkoutDays': total_workout_days,
            'totalVolume': f'{total_volume:.0f}',
            'mainFocusBodyPart': main_focus_body_part,
            'topExercises': top_exercises,
            'bestPerformance': period_best
        }

    def _empty_stats(self):
        return {'totalWorkoutDays': 0, 'totalVolume': 0, 'mainFocusBodyPart': NO_DATA, 'topExercises': [], 'bestPerformance': {'exercise': NO_DATA, 'weight': 0, 'reps': 0}}

    def _get_main_focus(self, db: Session, start_dt, end_dt):
        category_vol = db.query(models.ExerciseInfo.category, func.sum(models.WorkoutLog.volume).label('vol'))\
            .join(models.WorkoutLog, models.ExerciseInfo.id == models.WorkoutLog.exercise_id)\
            .filter(models.WorkoutLog.date.between(start_dt, end_dt))\
            .group_by(models.ExerciseInfo.category).order_by(func.sum(models.WorkoutLog.volume).desc()).first()
        return category_vol[0] if category_vol else NO_DATA

    def _get_top_exercises(self, db: Session, start_dt, end_dt):
        top_exercises_query = db.query(models.ExerciseInfo.name, func.sum(models.WorkoutLog.volume).label('vol'))\
            .join(models.WorkoutLog, models.ExerciseInfo.id == models.WorkoutLog.exercise_id)\
            .filter(models.WorkoutLog.date.between(start_dt, end_dt))\
            .group_by(models.ExerciseInfo.name).order_by(func.sum(models.WorkoutLog.volume).desc()).limit(5).all()
        return [{'exercise': name, 'volume': f'{volume:.0f}kg'} for name, volume in top_exercises_query]

    def _get_best_performance(self, db: Session, start_dt, end_dt):
        best_perf_log = db.query(models.WorkoutLog).join(models.ExerciseInfo)\
            .filter(models.WorkoutLog.date.between(start_dt, end_dt))\
            .order_by(models.WorkoutLog.weight.desc()).first()
        if best_perf_log:
            return {'exercise': best_perf_log.exercise.name, 'weight': best_perf_log.weight, 'reps': best_perf_log.reps_or_time}
        return {'exercise': NO_DATA, 'weight': 0.0, 'reps': 0.0}

    def _calculate_avg_workout_days(self, current_stats, weeks_in_period):
        if weeks_in_period > 0 and current_stats['totalWorkoutDays'] > 0:
            return round(current_stats['totalWorkoutDays'] / weeks_in_period)
        return 0

    def _calculate_pr(self, db: Session, current_stats, start_date):
        pr = {'exercise': NO_DATA, 'record': ''}
        if current_stats['bestPerformance']['weight'] > 0:
            best_exercise_name = current_stats['bestPerformance']['exercise']
            best_exercise = db.query(models.ExerciseInfo).filter(models.ExerciseInfo.name == best_exercise_name).first()
            if best_exercise:
                previous_best_weight = db.query(func.max(models.WorkoutLog.weight))\
                    .filter(models.WorkoutLog.exercise_id == best_exercise.id, models.WorkoutLog.date < start_date).scalar() or 0
                
                if current_stats['bestPerformance']['weight'] > previous_best_weight:
                    pr['exercise'] = best_exercise_name
                    pr['record'] = f"{current_stats['bestPerformance']['weight']:.1f}kg x {current_stats['bestPerformance']['reps']:.0f}회"
        return pr

    def _calculate_inbody_changes(self, db: Session, start_date, end_date):
        start_inbody = db.query(models.Inbody).filter(models.Inbody.date < start_date).order_by(models.Inbody.date.desc()).first()
        end_inbody = db.query(models.Inbody).filter(models.Inbody.date <= end_date).order_by(models.Inbody.date.desc()).first()
        if not end_inbody: end_inbody = start_inbody

        if end_inbody:
            start_w, start_m, start_f = (start_inbody.weight, start_inbody.muscle_mass, start_inbody.fat_percent) if start_inbody else (end_inbody.weight, end_inbody.muscle_mass, end_inbody.fat_percent)
            return {
                'endWeight': f"{end_inbody.weight} kg{self._get_change_str(end_inbody.weight, start_w)}",
                'endMuscleMass': f"{end_inbody.muscle_mass} kg{self._get_change_str(end_inbody.muscle_mass, start_m)}",
                'endBodyFatPercent': f"{end_inbody.fat_percent * 100:.1f}%{self._get_change_str(end_inbody.fat_percent, start_f)}"
            }
        return {'endWeight': 'N/A', 'endMuscleMass': 'N/A', 'endBodyFatPercent': 'N/A'}

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
            if diff > 0: return f' (+{diff:.2f}{UP_ARROW})'
            if diff < 0: return f' ({diff:.2f}{DOWN_ARROW})'
            return NO_CHANGE
        except (ValueError, TypeError):
            return ''
