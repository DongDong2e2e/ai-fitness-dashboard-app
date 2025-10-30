from datetime import datetime, timedelta
import json
from backend.app.config import Config
from backend.app.services.google_sheets import GoogleSheetsService
from backend.app.services.gemini_ai import GeminiAIService

class ReportGeneratorService:
    def __init__(self, spreadsheet_name: str):
        self.spreadsheet_name = spreadsheet_name
        self.gs_service = GoogleSheetsService()
        self.gemini_service = GeminiAIService()

from datetime import datetime, timedelta
import json
class ReportGeneratorService:
    def __init__(self):
        self.spreadsheet_name = Config.SPREADSHEET_NAME
        self.gs_service = GoogleSheetsService()
        self.gemini_service = GeminiAIService()

    def send_report(self, report_type: str):
        try:
            print(f"[{report_type}] 4단계 리포트 생성을 시작합니다.")
            log_sheet = self.gs_service.get_sheet_by_name(self.spreadsheet_name, Config.STRUCTURED_LOG_SHEET)
            inbody_sheet = self.gs_service.get_sheet_by_name(self.spreadsheet_name, Config.INBODY_SHEET)

            if not log_sheet or not inbody_sheet:
                raise ValueError("필수 시트를 찾을 수 없습니다.")

            stats = self.analyze_data_for_period(log_sheet, inbody_sheet, report_type)

            if stats['current']['totalWorkoutDays'] == 0:
                print(f"이번 {stats['periodName']} 운동 기록이 없어 리포트를 발송하지 않습니다.")
                return

            print(f"[{report_type}] 1단계: 과거 데이터 컨텍스트 요약 시작")
            history_context = "이전 기간의 운동 기록이 없습니다."
            if stats['previous']['totalWorkoutDays'] > 0:
                history_context = self.gemini_service.call_gemini_api(self._create_history_analysis_prompt(stats), 'text')

            print(f"[{report_type}] 2단계: 현재 데이터 심층 분석 시작")
            tactical_analysis = self.gemini_service.call_gemini_api(self._create_tactical_analysis_prompt(stats, history_context), 'text')

            print(f"[{report_type}] 3단계: 맞춤형 루틴 생성 시작")
            recommended_routine = self.gemini_service.call_gemini_api(self._create_routine_generation_prompt(stats, tactical_analysis), 'text')

            print(f"[{report_type}] 4단계: 최종 리포트 생성 시작")
            report_html = self.gemini_service.call_gemini_api(self._create_final_report_prompt(stats, report_type, tactical_analysis, recommended_routine), 'html')

            subject = f"💪 {Config.USER_NAME}님, {stats['periodName']} 운동 리포트 + 맞춤 루틴이 도착했습니다!"
            
            msg = MIMEText(report_html, 'html', 'utf-8')
            msg['Subject'] = subject
            msg['From'] = Config.SENDER_EMAIL
            msg['To'] = Config.REPORT_RECIPIENT_EMAIL

            with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as smtp:
                smtp.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
                smtp.send_message(msg)

            print(f"[{report_type}] 리포트 이메일을 성공적으로 발송했습니다.")

        except Exception as e:
            print(f"[{report_type}] 리포트 생성 오류: {e}")
            error_subject = f"🚨 [{report_type}] 운동 리포트 생성 오류"
            error_body = f"오류가 발생했습니다: {e}"
            error_msg = MIMEText(error_body, 'plain', 'utf-8')
            error_msg['Subject'] = error_subject
            error_msg['From'] = Config.SENDER_EMAIL
            error_msg['To'] = Config.REPORT_RECIPIENT_EMAIL
            with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as smtp:
                smtp.login(Config.SENDER_EMAIL, Config.SENDER_PASSWORD)
                smtp.send_message(error_msg)


    def analyze_data_for_period(self, log_sheet, inbody_sheet, period_type: str):
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        
        def format_date(date_obj): # Helper function for consistent date formatting
            return date_obj.strftime('%Y-%m-%d')

        start_date, end_date, prev_start_date, prev_end_date, period_name, weeks_in_period = (None,) * 6

        if period_type == 'week':
            end_date = today - timedelta(days=today.weekday() + 1) # Last Sunday
            start_date = end_date - timedelta(days=6) # Last Monday
            prev_end_date = start_date - timedelta(days=1)
            prev_start_date = prev_end_date - timedelta(days=6)
            period_name = '주간'
            weeks_in_period = 1
        elif period_type == 'month':
            end_date = today.replace(day=1) - timedelta(days=1) # Last day of previous month
            start_date = end_date.replace(day=1) # First day of previous month
            prev_end_date = start_date - timedelta(days=1)
            prev_start_date = prev_end_date.replace(day=1)
            period_name = f'{start_date.year}년 {start_date.month}월'
            weeks_in_period = 4.345
        elif period_type == 'quarter':
            current_quarter = (today.month - 1) // 3
            end_date = datetime(today.year, current_quarter * 3 + 1, 1) - timedelta(days=1) # Last day of previous quarter
            start_date = datetime(end_date.year, (end_date.month - 1) // 3 * 3 + 1, 1) # First day of previous quarter
            prev_end_date = start_date - timedelta(days=1)
            prev_start_date = datetime(prev_end_date.year, (prev_end_date.month - 1) // 3 * 3 + 1, 1)
            period_name = f'{start_date.year}년 {(start_date.month - 1) // 3 + 1}분기'
            weeks_in_period = 13
        elif period_type == 'year':
            last_year = today.year - 1
            end_date = datetime(last_year, 12, 31)
            start_date = datetime(last_year, 1, 1)
            prev_end_date = start_date - timedelta(days=1)
            prev_start_date = datetime(prev_end_date.year - 1, 1, 1)
            period_name = f'{last_year}년 연간'
            weeks_in_period = 52
        else:
            raise ValueError("Invalid period type")

        start_date_str = format_date(start_date)
        end_date_str = format_date(end_date)
        prev_start_date_str = format_date(prev_start_date)
        prev_end_date_str = format_date(prev_end_date)

        log_data_raw = log_sheet.get_all_values()
        inbody_data_raw = inbody_sheet.get_all_values()

        if not log_data_raw or len(log_data_raw) < 2: # Ensure there's at least a header and one data row
            log_data = []
        else:
            header = log_data_raw[0]
            log_data = log_data_raw[1:] # Skip header

        if not inbody_data_raw or len(inbody_data_raw) < 2:
            inbody_data = []
        else:
            inbody_data = inbody_data_raw[1:] # Skip header

        # Map headers to indices for easier access
        header_map = {
            '날짜': 0, '운동명': 1, '세트_구분': 2, '무게(kg)': 4, '횟수/시간': 5, 
            '단위': 6, '볼륨(kg)': 7, '대분류': 8
        }
        
        # Filter out warm-up sets and non-rep based exercises
        all_time_data = [ 
            row for row in log_data 
            if row[header_map['세트_구분']] != '웜업' and row[header_map['단위']] == '회'
        ]

        def extract_stats_for_period(start_str, end_str):
            period_data = [ 
                row for row in all_time_data 
                if start_str <= format_date(datetime.strptime(row[header_map['날짜']], '%Y-%m-%d')) <= end_str
            ]

            if not period_data:
                return {'totalWorkoutDays': 0, 'totalVolume': 0, 'mainFocusBodyPart': '없음', 'topExercises': [], 'bestPerformance': {'exercise': '없음', 'weight': 0, 'reps': 0}}

            workout_days = len(set(format_date(datetime.strptime(row[header_map['날짜']], '%Y-%m-%d')) for row in period_data)))
            total_volume = sum(float(row[header_map['볼륨(kg)']]) for row in period_data if row[header_map['볼륨(kg)']])

            category_vol = {}
            exercise_vol = {}
            for row in period_data:
                category = row[header_map['대분류']] or '미분류'
                exercise = row[header_map['운동명']]
                volume = float(row[header_map['볼륨(kg)']]) if row[header_map['볼륨(kg)']] else 0

                category_vol[category] = category_vol.get(category, 0) + volume
                exercise_vol[exercise] = exercise_vol.get(exercise, 0) + volume

            main_focus_body_part = max(category_vol, key=category_vol.get) if category_vol else '없음'
            top_exercises = sorted(exercise_vol.items(), key=lambda item: item[1], reverse=True)[:5]
            top_exercises_formatted = [{'exercise': name, 'volume': f'{volume:.0f}kg'} for name, volume in top_exercises]

            period_best = {'exercise': '없음', 'weight': 0.0, 'reps': 0.0}
            for row in period_data:
                weight = float(row[header_map['무게(kg)']]) if row[header_map['무게(kg)']] else 0.0
                if weight > period_best['weight']:
                    period_best = {
                        'exercise': row[header_map['운동명']],
                        'weight': weight,
                        'reps': float(row[header_map['횟수/시간']]) if row[header_map['횟수/시간']] else 0.0
                    }
            return {
                'totalWorkoutDays': workout_days,
                'totalVolume': f'{total_volume:.0f}',
                'mainFocusBodyPart': main_focus_body_part,
                'topExercises': top_exercises_formatted,
                'bestPerformance': period_best
            }

        current_stats = extract_stats_for_period(start_date_str, end_date_str)
        previous_stats = extract_stats_for_period(prev_start_date_str, prev_end_date_str)

        avg_workout_days_per_week = 0
        if current_stats['totalWorkoutDays'] > 0 and weeks_in_period > 0:
            avg_workout_days_per_week = max(1, round(current_stats['totalWorkoutDays'] / weeks_in_period))

        pr = {'exercise': '없음', 'record': ''}
        if current_stats['bestPerformance']['weight'] > 0:
            previous_all_data_for_exercise = [
                row for row in all_time_data
                if format_date(datetime.strptime(row[header_map['날짜']], '%Y-%m-%d')) < start_date_str
                and row[header_map['운동명']] == current_stats['bestPerformance']['exercise']
            ]
            previous_best_weight = 0.0
            if previous_all_data_for_exercise:
                previous_best_weight = max(float(row[header_map['무게(kg)']]) for row in previous_all_data_for_exercise if row[header_map['무게(kg)']])

            if current_stats['bestPerformance']['weight'] > previous_best_weight:
                pr['exercise'] = current_stats['bestPerformance']['exercise']
                pr['record'] = f'{current_stats['bestPerformance']['weight']:.1f}kg x {current_stats['bestPerformance']['reps']:.0f}회'

        # InBody data processing
        start_inbody = ['N/A'] * 6
        end_inbody = ['N/A'] * 6

        # Filter inbody data for the period before current_period_start_date
        inbody_before_current_period = [
            row for row in inbody_data
            if format_date(datetime.strptime(row[0], '%Y-%m-%d')) < start_date_str
        ]
        if inbody_before_current_period:
            start_inbody = inbody_before_current_period[-1]

        # Filter inbody data for the current period up to end_date
        inbody_up_to_end_date = [
            row for row in inbody_data
            if format_date(datetime.strptime(row[0], '%Y-%m-%d')) <= end_date_str
        ]
        if inbody_up_to_end_date:
            end_inbody = inbody_up_to_end_date[-1]
        else:
            end_inbody = start_inbody # If no inbody data in current period, use the last one before it

        def get_change(latest_val, prev_val):
            try:
                latest_val_f = float(latest_val)
                prev_val_f = float(prev_val)
                diff = latest_val_f - prev_val_f
                if diff > 0: return f' (+{diff:.2f} ▲)'
                if diff < 0: return f' ({diff:.2f} ▼)'
                return ' (변화 없음)'
            except (ValueError, TypeError):
                return ''

        def format_percent(val):
            try:
                return f'{float(val) * 100:.1f}%'
            except (ValueError, TypeError):
                return 'N/A'

        return {
            'userName': Config.USER_NAME,
            'periodName': period_name,
            'startDate': start_date_str,
            'endDate': end_date_str,
            'current': current_stats,
            'previous': previous_stats,
            'avgWorkoutDaysPerWeek': avg_workout_days_per_week,
            'prExercise': pr['exercise'],
            'prRecord': pr['record'],
            'endWeight': f'{end_inbody[2]} kg{get_change(end_inbody[2], start_inbody[2])}',
            'endMuscleMass': f'{end_inbody[3]} kg{get_change(end_inbody[3], start_inbody[3])}',
            'endBodyFatPercent': f'{format_percent(end_inbody[5])}{get_change(end_inbody[5], start_inbody[5])}'
        }

    def _create_history_analysis_prompt(self, stats: dict) -> str:
        return f"""**Persona:** 당신은 피트니스 데이터 기록 분석가 '아카이브'입니다. 당신의 임무는 과거 데이터를 객관적으로 요약하는 것입니다.
**Task:** 아래 {stats["userName"]}님의 **이전 기간** 운동 데이터를 간결하게 요약해주세요. 어떤 해석이나 조언도 하지 말고, 오직 사실만을 나열하세요.
**Input Data (Previous Period):**
- 총 운동일수: {stats["previous"]["totalWorkoutDays"]}일, 총 볼륨: {stats["previous"]["totalVolume"]} kg, 주력 운동 부위: {stats["previous"]["mainFocusBodyPart"]}, 볼륨 상위 운동: {json.dumps(stats["previous"]["topExercises"])}
**Output:** 이전 기간의 운동 패턴은 다음과 같음: [운동일수, 총 볼륨, 주력 부위, 상위 운동을 바탕으로 한 문장의 객관적인 요약]"""

    def _create_tactical_analysis_prompt(self, stats: dict, history_context: str) -> str:
        return f"""**Persona:** 당신은 전문 피트니스 데이터 분석가 '옵티머스'입니다.
**Task:** '아카이브'가 요약한 과거 데이터와 아래 제공된 현재 데이터를 **비교 분석**하여, {stats["userName"]}님의 성과에 대한 핵심 인사이트를 도출해주세요.
**Input Data 1: Historical Context (from 'Archive')**
{history_context}
**Input Data 2: Current Period Data ({stats["periodName"]}: {stats["startDate"]} ~ {stats["endDate"]})**
- 총 운동일수: {stats["current"]["totalWorkoutDays"]}일, 총 볼륨: {stats["current"]["totalVolume"]} kg, 주력 운동 부위: {stats["current"]["mainFocusBodyPart"]}, 볼륨 상위 운동: {json.dumps(stats["current"]["topExercises"])}
- 신기록(PR) 달성: {stats["prExercise"]} ({stats["prRecord"]})
- 인바디 변화 (이전 전체 기간 대비 현재): 체중: {stats["endWeight"]}, 골격근량: {stats["endMuscleMass"]}, 체지방률: {stats["endBodyFatPercent"]}
**Instructions:** 1. **Compare & Contrast:** 현재와 과거 데이터를 비교하여 변화된 패턴을 찾아내세요. 2. **Synthesize:** 이 변화가 인바디 결과나 PR 달성과 어떤 연관이 있는지 종합적으로 분석하세요. 3. **Conclude:** 분석을 바탕으로 칭찬할 점, 고려할 점, 다음을 위한 구체적인 제안을 도출하세요.
**Output Format:**
### 옵티머스의 데이터 분석 노트
**1. 성장 및 변화 포인트:** *[예: "이전 기간 대비 총 볼륨이 2,500kg 증가했으며, 이는 주력 부위인 하체 운동의 빈도가 늘어난 덕분으로 보입니다."]*
**2. 주목할 성과:** *[PR, 인바디의 긍정적 변화 등을 과거와 비교하며 구체적으로 칭찬]*
**3. 다음을 위한 전략 제안:** *[분석된 성장/정체 패턴을 기반으로 다음 기간의 목표를 구체적으로 제시]*"""

    def _create_routine_generation_prompt(self, stats: dict, tactical_analysis: str) -> str:
        return f"""**Persona:** 당신은 엘리트 스트렝스 코치 '스트라테고스'입니다.
**Task:** 아래 제공된 {stats["userName"]}님의 데이터 분석 결과를 바탕으로, 다음 주를 위한 **사용자의 평균 운동 빈도에 맞는 최적의 운동 루틴**을 추천해주세요. 루틴은 반드시 분석 결과에 명시된 '전략 제안'을 반영해야 합니다.
**Input Data 1: Athlete's Current Profile**
- 이름: {stats["userName"]}, **평균 주당 운동일수:** {stats["avgWorkoutDaysPerWeek"]}일, 주로 수행하는 운동: {json.dumps([e["exercise"] for e in stats["current"]["topExercises"]])}, 최근 PR: {stats["prExercise"]} {stats["prRecord"]}, 주력 운동 부위: {stats["current"]["mainFocusBodyPart"]}
**Input Data 2: Tactical Analysis (from 'Optimus')**
---
{tactical_analysis}
---
**Instructions:** 1. **Dynamic Split:** '{stats["avgWorkoutDaysPerWeek"]}일'에 맞춰 가장 이상적인 분할 루틴을 설계하세요. 2. **Goal-Oriented:** '전략 제안'을 최우선 목표로 설정하세요. 3. **Personalized:** 선호 운동을 참고하되, 약점 부위를 보완할 운동을 최소 1개 이상 포함시키세요. 4. **Progressive Overload:** 최근 PR 기록을 바탕으로 현실적인 무게와 횟수를 제안하세요. 5. **Clear Structure:** 각 Day별로 루틴을 명확하게 구분하고, '운동명: 무게 x 횟수, 0세트' 형식으로 제시하세요.
**Output Format:**
### 스트라테고스의 추천 주간 루틴
**목표:** [분석 결과의 '전략 제안'을 한 문장으로 요약]
**추천 분할:** [AI가 설계한 분할법]
**Day 1: [주요 부위]**
* ...
(사용자의 평균 운동일수에 맞춰 Day 개수를 동적으로 생성)"""

    def _create_final_report_prompt(self, stats: dict, report_type: str, tactical_analysis: str, recommended_routine: str) -> str:
        persona = f"You are a friendly and motivating personal trainer in Korea named '버니'. Your client is {stats["userName"]}."
        report_details = {
            'week': {'title': f'💪 {stats["userName"]}님의 주간 운동 리포트', 'intro': '지난 한 주도 정말 수고 많으셨어요! 땀 흘린 만큼 어떤 변화가 있었는지 함께 살펴볼까요?'},
            'month': {'title': f'🗓️ {stats["userName"]}님, {stats["periodName"]} 운동 리포트', 'intro': '한 달간의 노력이 쌓여 멋진 결과를 만들었어요.'},
            'quarter': {'title': f'📈 {stats["userName"]}님, {stats["periodName"]} 종합 리포트', 'intro': '지난 3개월의 꾸준함이 만든 놀라운 변화를 확인해 보세요.'},
            'year': {'title': f'🎉 {stats["userName"]}님, 경이로운 한 해를 돌아보며! {stats["periodName"]} 연간 리포트', 'intro': '1년 동안의 위대한 여정에 진심으로 박수를 보냅니다!'}
        }
        report_detail = report_details.get(report_type, report_details['week'])

        return f"""**Persona:** {persona}
**Task:** Create a comprehensive fitness report email in Korean for {stats["userName"]}, formatted in HTML. You must integrate the "Tactical Analysis" and "Recommended Routine".
**Input Data 1: Data Summary ({stats["periodName"]})**
- Period: {stats["startDate"]} ~ {stats["endDate"]}, Total workout days: {stats["current"]["totalWorkoutDays"]}, Main focus: {stats["current"]["mainFocusBodyPart"]}, Total volume: {stats["current"]["totalVolume"]} kg, New PR: {stats["prExercise"]} with {stats["prRecord"]}, InBody (Weight): {stats["endWeight"]}, InBody (Muscle): {stats["endMuscleMass"]}, InBody (Body Fat): {stats["endBodyFatPercent"]}
**Input Data 2: Tactical Analysis (from 'Optimus')**
---
{tactical_analysis}
---
**Input Data 3: Recommended Routine (from 'Strategos')**
---
{recommended_routine}
---
**Instructions:** 1. Use Title: "{report_detail["title"]}" and Intro: "{report_detail["intro"]}". 2. Rewrite "Tactical Analysis" in your friendly tone under "📊 버니의 성장 코멘트". 3. Create a new section "🎯 다음 주 추천 루틴" and format the "Recommended Routine" in HTML. 4. Write a motivating closing statement. 5. Use basic HTML and highlight changes (▲ green, ▼ red)."""
