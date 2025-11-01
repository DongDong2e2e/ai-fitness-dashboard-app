from sqlalchemy.orm import Session

from .. import prompts
from ..config import Config
from .gemini_ai import GeminiAIService
from .report_analyzer import ReportAnalyzer
from .email_service import EmailService

class ReportGeneratorService:
    def __init__(self):
        self.gemini_service = GeminiAIService()
        self.analyzer_service = ReportAnalyzer()
        self.email_service = EmailService()

    def send_report(self, report_type: str, db: Session):
        """Orchestrates the report generation and sending process."""
        try:
            print(f"[{report_type}] 리포트 생성을 시작합니다.")
            
            # 1. 데이터 분석
            stats = self.analyzer_service.analyze_data_for_period(db, report_type)
            if stats['current']['totalWorkoutDays'] == 0:
                print(f"이번 {stats['periodName']} 운동 기록이 없어 리포트를 발송하지 않습니다.")
                return

            # 2. AI를 이용한 리포트 내용 생성
            print(f"[{report_type}] 1단계: 과거 데이터 컨텍스트 요약 시작")
            history_context = "이전 기간의 운동 기록이 없습니다."
            if stats['previous']['totalWorkoutDays'] > 0:
                history_prompt = prompts.create_history_analysis_prompt(stats)
                history_context = self.gemini_service.call_gemini_api(history_prompt, 'text')

            print(f"[{report_type}] 2단계: 현재 데이터 심층 분석 시작")
            tactical_prompt = prompts.create_tactical_analysis_prompt(stats, history_context)
            tactical_analysis = self.gemini_service.call_gemini_api(tactical_prompt, 'text')

            print(f"[{report_type}] 3단계: 맞춤형 루틴 생성 시작")
            routine_prompt = prompts.create_routine_generation_prompt(stats, tactical_analysis)
            recommended_routine = self.gemini_service.call_gemini_api(routine_prompt, 'text')

            print(f"[{report_type}] 4단계: 최종 리포트 생성 시작")
            final_report_prompt = prompts.create_final_report_prompt(stats, report_type, tactical_analysis, recommended_routine)
            report_html = self.gemini_service.call_gemini_api(final_report_prompt, 'html')

            # 3. 이메일 발송
            subject = f"💪 {Config.USER_NAME}님, {stats['periodName']} 운동 리포트 + 맞춤 루틴이 도착했습니다!"
            self.email_service.send_email(subject, Config.REPORT_RECIPIENT_EMAIL, report_html)

            print(f"[{report_type}] 리포트 생성 및 발송 프로세스를 성공적으로 완료했습니다.")

        except Exception as e:
            print(f"[{report_type}] 리포트 생성 프로세스 중 오류 발생: {e}")