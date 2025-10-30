from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from backend.app.config import Config
from backend.app.services.google_sheets import GoogleSheetsService
from backend.app.services.gemini_ai import GeminiAIService
from backend.app.services.report_generator import ReportGeneratorService
from backend.app.services.chatbot_service import ChatbotService

# FastAPI 앱 생성
app = FastAPI()

# CORS 미들웨어 설정 (개발 중 프론트엔드からの接続を許可)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 프론트엔드 주소만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
google_sheets_service = GoogleSheetsService()
gemini_ai_service = GeminiAIService() # Although not directly used here, it's good to initialize
report_generator_service = ReportGeneratorService()
chatbot_service = ChatbotService(spreadsheet_name=Config.SPREADSHEET_NAME)

# 기본 경로 (서버가 살아있는지 확인용)
@app.get("/")
def read_root():
    return {"Hello": "Backend World"}

# 데이터 동기화 트리거 엔드포인트 (onEdit 트리거 대체)
@app.post("/update-data")
async def update_data():
    try:
        google_sheets_service.update_structured_log_sheet(spreadsheet_name=Config.SPREADSHEET_NAME) # Use Config.SPREADSHEET_NAME
        return {"message": "Structured log sheet updated successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update data: {e}")

# 리포트 생성 및 발송 트리거 엔드포인트
@app.post("/send-report/{report_type}")
async def send_report(report_type: str):
    if report_type not in ["week", "month", "quarter", "year"]:
        raise HTTPException(status_code=400, detail="Invalid report type. Must be 'week', 'month', 'quarter', or 'year'.")
    try:
        report_generator_service.send_report(report_type)
        return {"message": f"{report_type.capitalize()} report sent successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send {report_type} report: {e}")

# 챗봇 엔드포인트
@app.post("/chat")
async def chat_with_bot(message: dict):
    user_message = message.get("message")
    if not user_message:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    try:
        response = chatbot_service.process_user_message(user_message)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot processing failed: {e}")

# 프론트엔드가 데이터를 요청할 API 경로
@app.get("/api/dashboard-data")
async def get_dashboard_data():
    try:
        log_sheet = google_sheets_service.get_sheet_by_name(Config.SPREADSHEET_NAME, Config.STRUCTURED_LOG_SHEET)
        inbody_sheet = google_sheets_service.get_sheet_by_name(Config.SPREADSHEET_NAME, Config.INBODY_SHEET)

        three_months_ago = datetime.now() - timedelta(days=90)
        
        def format_date(date_obj):
            return date_obj.strftime('%Y-%m-%d')

        log_data_raw = log_sheet.get_all_values()
        inbody_data_raw = inbody_sheet.get_all_values()

        if not log_data_raw or len(log_data_raw) < 2:
            log_data = []
        else:
            log_data = [row for row in log_data_raw[1:] if row[0] and datetime.strptime(row[0], '%Y-%m-%d') >= three_months_ago]

        if not inbody_data_raw or len(inbody_data_raw) < 2:
            inbody_data = []
        else:
            inbody_data = [row for row in inbody_data_raw[1:] if row[0] and datetime.strptime(row[0], '%Y-%m-%d') >= three_months_ago]

        def extract_workout_data(exercise_list):
            workout_data = {}
            for exercise_name in exercise_list:
                exercise_logs = [row for row in log_data if row[1] and exercise_name in row[1]]
                if not exercise_logs:
                    continue
                
                daily_max = {}
                for row in exercise_logs:
                    try:
                        date_str = format_date(datetime.strptime(row[0], '%Y-%m-%d'))
                        weight = float(row[4])
                        if date_str not in daily_max or weight > daily_max[date_str]:
                            daily_max[date_str] = weight
                    except (ValueError, IndexError):
                        continue
                
                sorted_dates = sorted(daily_max.keys())
                workout_data[exercise_name] = {"labels": sorted_dates, "data": [daily_max[date] for date in sorted_dates]}
            return workout_data

        push_exercises = ['벤치프레스', '덤벨 숄더 프레스', '인클라인 체스트 프레스']
        pull_exercises = ['루마니안 데드리프트', '티바 로우']
        leg_exercises = ['레그 프레스', '브이 스쿼트', '리버스 브이 스쿼트', '힙 쓰러스트']
        
        push_data = extract_workout_data(push_exercises)
        pull_data = extract_workout_data(pull_exercises)
        leg_data = extract_workout_data(leg_exercises)

        inbody_chart_data = {
            "labels": [format_date(datetime.strptime(row[0], '%Y-%m-%d')) for row in inbody_data if row[0]],
            "weight": [float(row[2]) for row in inbody_data if row[2]],
            "muscle": [float(row[3]) for row in inbody_data if row[3]],
            "fatPercent": [float(row[5]) * 100 for row in inbody_data if row[5]]
        }

        return {"pushData": push_data, "pullData": pull_data, "legData": leg_data, "inbodyData": inbody_chart_data}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve dashboard data: {e}")
