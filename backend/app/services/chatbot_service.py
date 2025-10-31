from datetime import datetime, timedelta
import json
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from backend.app import models, prompts
from backend.app.services.gemini_ai import GeminiAIService

class ChatbotService:
    def __init__(self):
        self.gemini_service = GeminiAIService()

    def process_user_message(self, message: str, db: Session):
        try:
            tool_calls = self._route_query_to_tools(message)
            if not tool_calls:
                # 도구가 필요 없는 일반 대화
                final_answer = self._generate_final_response(message, "")
                return {'type': 'text', 'content': final_answer}

            # 차트 생성 도구 확인
            chart_tool_call = next((call for call in tool_calls if call.get('tool') == 'generate_chart'), None)
            if chart_tool_call:
                chart_data = self._find_chart_data(chart_tool_call['params'], db)
                return {'type': 'chart', 'data': chart_data, 'title': f"{chart_tool_call['params'].get('exercise_name', '')} {chart_tool_call['params'].get('metric', '')} 변화"}

            retrieved_data = self._execute_tool_calls(tool_calls, db)
            final_answer = self._generate_final_response(message, retrieved_data)
            return {'type': 'text', 'content': final_answer}
        except Exception as e:
            print(f"챗봇 오류: {e}")
            return {'type': 'text', 'content': f"처리 중 오류가 발생했습니다: {e}"}

    def _route_query_to_tools(self, message: str) -> list:
        today = datetime.now().strftime('%Y-%m-%d')
        prompt = prompts.get_routing_prompt(message, today)
        result_text = self.gemini_service.call_gemini_api(prompt, 'text').replace('```json\n', '').replace('\n```', '').strip()
        print(f"1단계 - 라우팅 결과 (JSON): {result_text}")
        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            return []

    def _execute_tool_calls(self, tool_calls: list, db: Session):
        if not tool_calls:
            return "검색할 특정 데이터가 없습니다. 일반적인 대화를 나눠주세요."

        results = []
        for call in tool_calls:
            tool_name = call.get('tool')
            params = call.get('params', {})
            result = f"[Tool: {tool_name}에 대한 결과]\n"
            try:
                if tool_name == 'search_workout_logs':
                    result += self._find_workout_data(params, db)
                elif tool_name == 'search_inbody_records':
                    result += self._find_inbody_data(params, db)
                else:
                    result += "알 수 없는 도구입니다."
            except Exception as e:
                result += f"도구 실행 중 오류 발생: {e}"
            results.append(result)
        
        aggregated_result = "\n\n".join(results)
        print(f"2단계 - 도구 실행 및 결과 취합:\n{aggregated_result}")
        return aggregated_result

    def _find_workout_data(self, conditions: dict, db: Session) -> str:
        query = db.query(models.WorkoutLog).join(models.ExerciseInfo)

        if conditions.get("exercise_names"):
            query = query.filter(models.ExerciseInfo.name.in_(conditions["exercise_names"]))

        if conditions.get("date_range_start") and conditions.get("date_range_end"):
            start_date = datetime.strptime(conditions["date_range_start"], "%Y-%m-%d").date()
            end_date = datetime.strptime(conditions["date_range_end"], "%Y-%m-%d").date()
            query = query.filter(models.WorkoutLog.date.between(start_date, end_date))

        filtered_logs = query.all()
        if not filtered_logs:
            return "해당 조건의 운동 기록을 찾지 못했습니다."

        metric = conditions.get("metric")
        if metric == "highest_weight":
            best_set = query.order_by(models.WorkoutLog.weight.desc()).first()
            if best_set:
                return f"최고 기록: {best_set.exercise.name} {best_set.weight:.1f}kg x {int(best_set.reps_or_time)}회 ({best_set.date.strftime('%Y-%m-%d')})"
            else:
                return "최고 기록을 찾지 못했습니다."
        elif metric == "total_volume":
            total_volume = query.with_entities(func.sum(models.WorkoutLog.volume)).scalar()
            return f"총 볼륨: {total_volume or 0:.0f} kg ({len(filtered_logs)} 세트)"
        
        # 기본: 최근 30개 기록 반환
        recent_logs = query.order_by(models.WorkoutLog.date.desc()).limit(30).all()
        formatted_records = [
            f"{log.date.strftime('%Y-%m-%d')}: {log.exercise.name} {log.weight:.1f}kg x {int(log.reps_or_time)}회"
            for log in recent_logs
        ]
        return "검색된 기록 ({}개 중 최근 {}개):\n{}".format(len(filtered_logs), len(recent_logs), "\n".join(formatted_records))

    def _find_inbody_data(self, conditions: dict, db: Session) -> str:
        query = db.query(models.Inbody)

        if conditions.get("date_range_start") and conditions.get("date_range_end"):
            start_date = datetime.strptime(conditions["date_range_start"], "%Y-%m-%d").date()
            end_date = datetime.strptime(conditions["date_range_end"], "%Y-%m-%d").date()
            query = query.filter(models.Inbody.date.between(start_date, end_date))

        filtered_data = query.order_by(models.Inbody.date.asc()).all()
        if not filtered_data:
            return "해당 기간의 인바디 기록을 찾지 못했습니다."

        def format_record(record: models.Inbody):
            return f"{record.date.strftime('%Y-%m-%d')}: 체중 {record.weight:.1f}kg, 골격근량 {record.muscle_mass:.1f}kg, 체지방률 {record.fat_percent * 100:.1f}%"

        metric = conditions.get("metric")
        if metric == 'latest':
            return f"가장 최근 기록: {format_record(filtered_data[-1])}"
        elif metric == 'change':
            if len(filtered_data) < 2:
                return "기간 내 변화를 분석하기에는 기록이 부족합니다."
            start_record = format_record(filtered_data[0])
            end_record = format_record(filtered_data[-1])
            muscle_change = filtered_data[-1].muscle_mass - filtered_data[0].muscle_mass
            return f"기간 내 변화:\n- 시작: {start_record}\n- 종료: {end_record}\n- 골격근량 변화: {muscle_change:+.2f}kg"
        
        return "\n".join([format_record(row) for row in filtered_data])

    def _find_chart_data(self, params: dict, db: Session) -> dict:
        exercise_name = params.get("exercise_name")
        metric = params.get("metric")

        exercise = db.query(models.ExerciseInfo).filter(models.ExerciseInfo.name == exercise_name).first()
        if not exercise:
            return {"labels": [], "data": []}

        if metric == 'max_weight':
            query = db.query(
                models.WorkoutLog.date,
                func.max(models.WorkoutLog.weight).label("metric")
            ).filter(models.WorkoutLog.exercise_id == exercise.id).group_by(models.WorkoutLog.date).order_by(models.WorkoutLog.date.asc())
        elif metric == 'total_volume':
            query = db.query(
                models.WorkoutLog.date,
                func.sum(models.WorkoutLog.volume).label("metric")
            ).filter(models.WorkoutLog.exercise_id == exercise.id).group_by(models.WorkoutLog.date).order_by(models.WorkoutLog.date.asc())
        else:
            return {"labels": [], "data": []}

        results = query.all()
        
        return {
            "labels": [res.date.strftime('%Y-%m-%d') for res in results],
            "data": [res.metric for res in results]
        }

    def _generate_final_response(self, message: str, retrieved_data: str) -> str:
        prompt = prompts.get_final_response_prompt(message, retrieved_data)
        return self.gemini_service.call_gemini_api(prompt, 'text')
