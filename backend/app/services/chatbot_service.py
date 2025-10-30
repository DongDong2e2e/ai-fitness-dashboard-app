from datetime import datetime, timedelta
import json
import re
from backend.app.config import Config
from backend.app.services.google_sheets import GoogleSheetsService
from backend.app.services.gemini_ai import GeminiAIService

class ChatbotService:
    def __init__(self, spreadsheet_name: str):
        self.spreadsheet_name = spreadsheet_name
        self.gs_service = GoogleSheetsService()
        self.gemini_service = GeminiAIService()

    def process_user_message(self, message: str):
        try:
            tool_calls = self._route_query_to_tools(message)
            
            # Check if any tool call is for chart generation
            chart_tool_call = next((call for call in tool_calls if call.get('tool') == 'generate_chart'), None)
            if chart_tool_call:
                chart_data = self._find_chart_data(chart_tool_call['params'])
                return {'type': 'chart', 'data': chart_data, 'title': f'{chart_tool_call['params'].get("exercise_name", "")} {chart_tool_call['params'].get("metric", "")} 변화'}

            retrieved_data = self._execute_tool_calls(tool_calls)
            final_answer = self._generate_final_response(message, retrieved_data)
            return {'type': 'text', 'content': final_answer}
        except Exception as e:
            print(f"챗봇 오류: {e}")
            return {'type': 'text', 'content': f"처리 중 오류가 발생했습니다: {e}"}

    def _route_query_to_tools(self, message: str) -> list:
        today = datetime.now().strftime('%Y-%m-%d')
        prompt = f"""**Persona:** 당신은 사용자의 질문을 분석하여 필요한 '도구'를 결정하는 '라우터' AI입니다.
**Task:** 사용자의 질문을 분석하여, 답변에 필요한 '도구(tool)'와 '파라미터(params)'를 JSON 배열 형식으로 반환하세요.
**Available Tools:**
1. `search_workout_logs`: 운동 기록(무게, 횟수, 볼륨 등)에 대한 텍스트 질문에 사용.
   - `params`: `{{"exercise_names": ["운동명"], "date_range_start": "YYYY-MM-DD", "date_range_end": "YYYY-MM-DD", "metric": "highest_weight" | "total_volume" | null}}`
2. `search_inbody_records`: 인바디 기록에 대한 텍스트 질문에 사용.
   - `params`: `{{"date_range_start": "YYYY-MM-DD", "date_range_end": "YYYY-MM-DD", "metric": "latest" | "change" | null}}`
3. `generate_chart`: '그래프로 보여줘', '차트로 알려줘', '추이' 등 시각화 요청 시 사용.
   - `params`: `{{"exercise_name": "운동명", "metric": "max_weight" | "total_volume"}}`
**Rules:**
- 날짜 관련 표현(지난주, 이번달 등)은 오늘({today})을 기준으로 'YYYY-MM-DD' 형식으로 정확히 계산해야 합니다.
- **'그래프', '차트', '추이' 등의 단어가 있으면 반드시 `generate_chart` 도구를 사용하세요.**
- 관련 도구가 없으면 빈 배열 `[]`을 반환하세요.
[실제 분석 요청] 질문: "{message}" -> JSON:"""
        result_text = self.gemini_service.call_gemini_api(prompt, 'text').replace('```json\n', '').replace('\n```', '').strip()
        print(f"1단계 - 라우팅 결과 (JSON): {result_text}")
        try:
            return json.loads(result_text)
        except json.JSONDecodeError:
            return []

    def _execute_tool_calls(self, tool_calls: list):
        if not tool_calls:
            return "검색할 특정 데이터가 없습니다. 일반적인 대화를 나눠주세요."

        results = []
        for call in tool_calls:
            tool_name = call.get('tool')
            params = call.get('params', {})
            result = f"[Tool: {tool_name}에 대한 결과]\n"
            try:
                if tool_name == 'search_workout_logs':
                    result += self._find_workout_data(params)
                elif tool_name == 'search_inbody_records':
                    result += self._find_inbody_data(params)
                elif tool_name == 'generate_chart':
                    chart_data = self._find_chart_data(params)
                    # For chart generation, we return a special dictionary
                    return {'type': 'chart', 'data': chart_data, 'title': f'{params.get("exercise_name", "")} {params.get("metric", "")} 변화'}
                else:
                    result += "알 수 없는 도구입니다."
            except Exception as e:
                result += f"도구 실행 중 오류 발생: {e}"
            results.append(result)
        
        aggregated_result = "\n\n".join(results)
        print(f"2단계 - 도구 실행 및 결과 취합:\n{aggregated_result}")
        return aggregated_result

    def _find_workout_data(self, conditions: dict) -> str:
        log_sheet = self.gs_service.get_sheet_by_name(self.spreadsheet_name, Config.STRUCTURED_LOG_SHEET)
        all_data = log_sheet.get_all_values()

        if not all_data or len(all_data) < 2: # Ensure there's at least a header and one data row
            return "운동 기록을 찾지 못했습니다."

        header = all_data[0]
        data_rows = all_data[1:]

        # Map headers to indices for easier access
        header_map = {
            '날짜': header.index('날짜'),
            '운동명': header.index('운동명'),
            '세트_구분': header.index('세트_구분'),
            '무게(kg)': header.index('무게(kg)'),
            '횟수/시간': header.index('횟수/시간'),
            '단위': header.index('단위'),
            '볼륨(kg)': header.index('볼륨(kg)')
        }

        filtered_data = data_rows

        if conditions.get("exercise_names") and len(conditions["exercise_names"]) > 0:
            filtered_data = [row for row in filtered_data if any(name in row[header_map['운동명']] for name in conditions["exercise_names"])]

        if conditions.get("date_range_start") and conditions.get("date_range_end"):
            start_date = datetime.strptime(conditions["date_range_start"], "%Y-%m-%d")
            end_date = datetime.strptime(conditions["date_range_end"], "%Y-%m-%d")
            filtered_data = [row for row in filtered_data if start_date <= datetime.strptime(row[header_map['날짜']], "%Y-%m-%d") <= end_date]

        if not filtered_data:
            return "해당 조건의 운동 기록을 찾지 못했습니다."

        metric = conditions.get("metric")
        if metric == "highest_weight":
            best_set = None
            max_weight = 0.0
            for row in filtered_data:
                try:
                    weight = float(row[header_map['무게(kg)']])
                    if weight > max_weight:
                        max_weight = weight
                        best_set = row
                except ValueError:
                    continue
            if best_set:
                return f"최고 기록: {best_set[header_map['운동명']]} {float(best_set[header_map['무게(kg)']]):.1f}kg x {int(float(best_set[header_map['횟수/시간']]))}회 ({datetime.strptime(best_set[header_map['날짜']], '%Y-%m-%d').strftime('%Y-%m-%d')})"
            else:
                return "최고 기록을 찾지 못했습니다."
        elif metric == "total_volume":
            total_volume = 0.0
            for row in filtered_data:
                try:
                    volume = float(row[header_map['볼륨(kg)']])
                    total_volume += volume
                except ValueError:
                    continue
            return f"총 볼륨: {total_volume:.0f} kg ({len(filtered_data)} 세트)"
        
        # Default case: return recent records
        sliced_data = filtered_data[-30:]
        formatted_records = []
        for row in sliced_data:
            try:
                date_str = datetime.strptime(row[header_map['날짜']], '%Y-%m-%d').strftime('%Y-%m-%d')
                exercise_name = row[header_map['운동명']]
                weight = float(row[header_map['무게(kg)']])
                reps = int(float(row[header_map['횟수/시간']]))
                formatted_records.append(f"{date_str}: {exercise_name} {weight:.1f}kg x {reps}회")
            except ValueError:
                continue
        return "검색된 기록 ({}개 중 최근 {}개):\n{}".format(len(filtered_data), len(sliced_data), "\n".join(formatted_records))

    def _find_inbody_data(self, conditions: dict) -> str:
        inbody_sheet = self.gs_service.get_sheet_by_name(self.spreadsheet_name, Config.INBODY_SHEET)
        all_data = inbody_sheet.get_all_values()

        if not all_data or len(all_data) < 2:
            return "인바디 기록을 찾지 못했습니다."

        data_rows = all_data[1:] # Skip header

        filtered_data = data_rows

        if conditions.get("date_range_start") and conditions.get("date_range_end"):
            start_date = datetime.strptime(conditions["date_range_start"], "%Y-%m-%d")
            end_date = datetime.strptime(conditions["date_range_end"], "%Y-%m-%d")
            filtered_data = [row for row in filtered_data if start_date <= datetime.strptime(row[0], "%Y-%m-%d") <= end_date]

        if not filtered_data:
            return "해당 기간의 인바디 기록을 찾지 못했습니다."

        def format_record(row):
            try:
                date_str = datetime.strptime(row[0], '%Y-%m-%d').strftime('%Y-%m-%d')
                weight = float(row[2])
                muscle = float(row[3])
                fat_percent = float(row[5]) * 100
                return f"{date_str}: 체중 {weight:.1f}kg, 골격근량 {muscle:.1f}kg, 체지방률 {fat_percent:.1f}%"
            except (ValueError, IndexError):
                return "잘못된 인바디 기록 형식입니다."

        metric = conditions.get("metric")
        if metric == 'latest':
            return f"가장 최근 기록: {format_record(filtered_data[-1])}"
        elif metric == 'change':
            if len(filtered_data) < 2:
                return "기간 내 변화를 분석하기에는 기록이 부족합니다."
            start_record = format_record(filtered_data[0])
            end_record = format_record(filtered_data[-1])
            try:
                muscle_change = float(filtered_data[-1][3]) - float(filtered_data[0][3])
                return f"기간 내 변화:\n- 시작: {start_record}\n- 종료: {end_record}\n- 골격근량 변화: {muscle_change:.2f}kg"
            except ValueError:
                return "인바디 기록 변화 분석 중 오류가 발생했습니다."
        
        return "\n".join([format_record(row) for row in filtered_data])

    def _find_chart_data(self, params: dict) -> dict:
        log_sheet = self.gs_service.get_sheet_by_name(self.spreadsheet_name, Config.STRUCTURED_LOG_SHEET)
        all_data = log_sheet.get_all_values()

        if not all_data or len(all_data) < 2:
            return {"labels": [], "data": []}

        header = all_data[0]
        data_rows = all_data[1:]

        header_map = {
            '날짜': header.index('날짜'),
            '운동명': header.index('운동명'),
            '무게(kg)': header.index('무게(kg)'),
            '볼륨(kg)': header.index('볼륨(kg)')
        }

        exercise_logs = [row for row in data_rows if row[header_map['운동명']] and params["exercise_name"] in row[header_map['운동명']]]

        if not exercise_logs:
            return {"labels": [], "data": []}

        daily_metrics = {}
        for row in exercise_logs:
            try:
                date_str = datetime.strptime(row[header_map['날짜']], '%Y-%m-%d').strftime('%Y-%m-%d')
                daily_metrics.setdefault(date_str, {'max_weight': 0.0, 'total_volume': 0.0})

                if params["metric"] == 'max_weight':
                    weight = float(row[header_map['무게(kg)']])
                    if weight > daily_metrics[date_str]['max_weight']:
                        daily_metrics[date_str]['max_weight'] = weight
                elif params["metric"] == 'total_volume':
                    volume = float(row[header_map['볼륨(kg)']])
                    daily_metrics[date_str]['total_volume'] += volume
            except (ValueError, IndexError):
                continue

        sorted_dates = sorted(daily_metrics.keys())
        data = [daily_metrics[date][params["metric"]] for date in sorted_dates]

        return {"labels": sorted_dates, "data": data}

    def _generate_final_response(self, message: str, retrieved_data: str) -> str:
        prompt = f"""**Persona:** 당신은 사용자의 운동 기록을 모두 알고 있는 친절한 AI 피트니스 비서 '버니'입니다. 항상 한국어로, 격려하는 말투로 답변해주세요.
**Task:** 사용자의 질문에 대해, 제공된 '검색된 데이터'를 반드시 종합적으로 참고하여 답변을 생성해주세요.
**User's Question:** "{message}"
**Retrieved Context (Data from Tools):**
---
{retrieved_data}
---
**Instruction:**
- 제공된 데이터를 바탕으로 질문에 대해 상세하고 친절하게 답변해주세요.
- 여러 도구의 결과가 있다면, 자연스럽게 연결하여 하나의 이야기처럼 설명해주세요.
- 기록에 없는 내용은 "기록을 찾아봤는데, 그 정보는 없었어요."라고 솔직하게 말해주세요.
**Answer (in Korean):"""
        return self.gemini_service.call_gemini_api(prompt, 'text')
