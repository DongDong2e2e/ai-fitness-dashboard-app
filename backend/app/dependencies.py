from .services.report_generator import ReportGeneratorService
from .services.dashboard_service import DashboardService
from .services.chatbot_service import ChatbotService


def get_report_generator_service() -> ReportGeneratorService:
    return ReportGeneratorService()

def get_dashboard_service() -> DashboardService:
    return DashboardService()

def get_chatbot_service() -> ChatbotService:
    return ChatbotService()
