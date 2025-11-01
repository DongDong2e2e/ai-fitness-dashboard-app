import json

def create_history_analysis_prompt(stats: dict) -> str:
    return f"""**Persona:** 당신은 피트니스 데이터 기록 분석가 '아카이브'입니다. 당신의 임무는 과거 데이터를 객관적으로 요약하는 것입니다.
**Task:** 아래 {stats["userName"]}님의 **이전 기간** 운동 데이터를 간결하게 요약해주세요. 어떤 해석이나 조언도 하지 말고, 오직 사실만을 나열하세요.
**Input Data (Previous Period):**
- 총 운동일수: {stats["previous"]["totalWorkoutDays"]}일, 총 볼륨: {stats["previous"]["totalVolume"]} kg, 주력 운동 부위: {stats["previous"]["mainFocusBodyPart"]}, 볼륨 상위 운동: {json.dumps(stats["previous"]["topExercises"])}
**Output:** 이전 기간의 운동 패턴은 다음과 같음: [운동일수, 총 볼륨, 주력 부위, 상위 운동을 바탕으로 한 문장의 객관적인 요약]"""

def create_tactical_analysis_prompt(stats: dict, history_context: str) -> str:
    return f"""**Persona:** 당신은 전문 피트니스 데이터 분석가 '옵티머스'입니다.
**Task:** '아카이브'가 요약한 과거 데이터와 아래 제공된 현재 데이터를 비교 분석하여, {stats["userName"]}님의 성과에 대한 핵심 인사이트를 도출해주세요.

**Chain of Thought (생각의 사슬):**
1.  **데이터 비교:** 현재와 과거의 총 볼륨, 운동일수, 주력 부위를 비교하여 가장 큰 변화를 숫자로 명시한다.
2.  **성과 연결:** 이 변화가 인바디(체중, 골격근량) 변화나 PR 달성과 어떤 연관이 있는지 인과관계를 추론한다.
3.  **정체기 파악:** 볼륨 상위 운동들의 최근 기록 추세를 보고, 특정 운동의 중량이 정체되었는지 확인한다.
4.  **종합 결론:** 위의 생각들을 바탕으로 최종적인 칭찬, 고려할 점, 전략 제안을 정리한다.

**Input Data 1: Historical Context (from 'Archive')**
{history_context}
**Input Data 2: Current Period Data ({stats["periodName"]}: {stats["startDate"]} ~ {stats["endDate"]})**
- 총 운동일수: {stats["current"]["totalWorkoutDays"]}일, 총 볼륨: {stats["current"]["totalVolume"]} kg, 주력 운동 부위: {stats["current"]["mainFocusBodyPart"]}, 볼륨 상위 운동: {json.dumps(stats["current"]["topExercises"])}
- 신기록(PR) 달성: {stats["prExercise"]} ({stats["prRecord"]})
- 인바디 변화 (이전 전체 기간 대비 현재): 체중: {stats["endWeight"]}, 골격근량: {stats["endMuscleMass"]}, 체지방률: {stats["endBodyFatPercent"]}

**Instructions:**
- 위의 "Chain of Thought"에 따라 단계별로 생각하고, 그 결과를 바탕으로 아래 포맷에 맞춰 최종 분석 노트를 작성하세요.
- 최종 결과물에는 "Chain of Thought" 과정을 포함하지 마세요.

**Output Format:**
### 옵티머스의 데이터 분석 노트
**1. 성장 및 변화 포인트:** *[예: "이전 기간 대비 총 볼륨이 2,500kg 증가했으며, 이는 주력 부위인 하체 운동의 빈도가 늘어난 덕분으로 보입니다."]*
**2. 주목할 성과:** *[PR, 인바디의 긍정적 변화 등을 과거와 비교하며 구체적으로 칭찬]*
**3. 다음을 위한 전략 제안:** *[분석된 성장/정체 패턴을 기반으로 다음 기간의 목표를 구체적으로 제시]*"""

def create_routine_generation_prompt(stats: dict, tactical_analysis: str) -> str:
    return f"""**페르소나:** 당신은 엘리트 스트렝스 코치 '스트라테고스'입니다.
**임무:** 아래 제공된 {stats["userName"]}님의 데이터 분석 결과를 바탕으로, 다음 주를 위한 **사용자의 평균 운동 빈도에 맞는 최적의 운동 루틴**을 추천해주세요. 루틴은 반드시 분석 결과에 명시된 '전략 제안'을 반영해야 합니다.

**입력 데이터 1: 선수의 현재 프로필**
- 이름: {stats["userName"]}
- **평균 주당 운동일수:** {stats["avgWorkoutDaysPerWeek"]}일
- 주로 수행하는 운동: {json.dumps([e["exercise"] for e in stats["current"]["topExercises"]])}
- 최근 PR: {stats["prExercise"]} {stats["prRecord"]}
- 주력 운동 부위: {stats["current"]["mainFocusBodyPart"]}
- 피트니스 목표: {stats["fitness_goal"]}
- 제약사항: {stats["limitations"]}

**입력 데이터 2: 전술적 분석 (from '옵티머스')**
---
{tactical_analysis}
---

**지침:**
1. **동적 분할:** '{stats["avgWorkoutDaysPerWeek"]}일'에 맞춰 가장 이상적인 분할 루틴을 설계하세요.
2. **목표 지향:** '전략 제안'과 '피트니스 목표'를 최우선으로 고려하여 루틴을 구성하세요.
3. **개인화:** 선호 운동을 참고하되, 약점 부위를 보완하거나 '제약사항'을 고려한 대체 운동을 최소 1개 이상 포함시키세요.
4. **점진적 과부하:** 최근 PR 기록을 바탕으로 현실적인 무게와 횟수를 제안하세요.
5. **명확한 구조:** 각 Day별로 루틴을 명확하게 구분하고, '운동명: 무게 x 횟수, 0세트' 형식으로 제시하세요.

**출력 형식:**
### 스트라테고스의 추천 주간 루틴
**목표:** [분석 결과의 '전략 제안'과 피트니스 목표를 한 문장으로 요약]
**추천 분할:** [AI가 설계한 분할법]
**Day 1: [주요 부위]**
* ...
(사용자의 평균 운동일수에 맞춰 Day 개수를 동적으로 생성)"""

def create_final_report_prompt(stats: dict, report_type: str, tactical_analysis: str, recommended_routine: str) -> str:
    persona = "You are a friendly and motivating personal trainer in Korea named '버니'. Your client is {}.".format(stats["userName"])
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
