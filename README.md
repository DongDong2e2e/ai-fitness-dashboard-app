# AI Fitness Dashboard App

## 프로젝트 개요

이 프로젝트는 Google Sheets와 Google Apps Script(GAS)로 구현되었던 운동 기록 관리 및 AI 리포트 자동 생성 서비스를 현대적인 웹 스택으로 마이그레이션한 애플리케이션입니다. 사용자의 운동 기록을 데이터베이스화하고, Gemini AI를 활용하여 주간/월간/분기/연간 맞춤형 리포트를 생성하여 이메일로 발송합니다. 또한, 대시보드와 챗봇 기능을 통해 운동 데이터를 시각적으로 확인하고 AI와 상호작용할 수 있습니다.

## 주요 기능

- **운동 기록 관리:** Google Sheets에 입력된 운동 데이터를 구조화하여 저장하고 관리합니다.
- **AI 기반 리포트:** Gemini AI를 활용하여 개인화된 운동 분석 리포트(주간, 월간, 분기, 연간)를 생성하고 지정된 이메일로 자동 발송합니다.
- **맞춤형 운동 루틴 제안:** AI 분석을 기반으로 사용자에게 최적화된 운동 루틴을 추천합니다.
- **대시보드:** 운동 볼륨, 최고 기록, 인바디 변화 등 핵심 데이터를 시각적으로 제공합니다.
- **챗봇:** 운동 기록 및 인바디 데이터에 대한 질문에 AI가 답변하고, 필요한 경우 차트를 생성하여 보여줍니다.

## 기술 스택

- **백엔드:** Python, FastAPI
- **프론트엔드:** React (JavaScript/TypeScript)
- **데이터베이스:** Google Sheets
- **AI:** Google Gemini API
- **배포:** Docker, Docker Compose

## 마이그레이션 배경

기존 Google Apps Script 기반의 서비스를 보다 유연하고 확장 가능한 아키텍처로 전환하기 위해 Python(FastAPI) 백엔드와 React 프론트엔드를 도입했습니다. 이를 통해 개발 생산성을 높이고, 다양한 환경에서의 배포 및 관리를 용이하게 합니다.

## 프로젝트 설정 및 실행

프로젝트를 로컬에서 실행하기 위한 단계별 가이드입니다.

### 1. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 환경 변수들을 설정해야 합니다. 민감한 정보이므로 `.gitignore`에 추가되어 있습니다.

```dotenv
# Gemini API Key
GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# Report Recipient Email
REPORT_RECIPIENT_EMAIL="your_email@example.com"

# User Name for Reports
USER_NAME="사용자이름"

# Google Spreadsheet Configuration
SPREADSHEET_NAME="AI_Fitness_Dashboard" # Google Sheets에 있는 스프레드시트의 정확한 이름

# Google Cloud Platform Service Account Credentials (for gspread)
# JSON 키 파일 내용을 직접 입력하거나, 파일 경로를 GOOGLE_APPLICATION_CREDENTIALS에 지정
GCP_TYPE="service_account"
GCP_PROJECT_ID="your-gcp-project-id"
GCP_PRIVATE_KEY_ID="your-private-key-id"
GCP_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_CONTENT_LINE1\nYOUR_PRIVATE_KEY_CONTENT_LINE2\n-----END PRIVATE KEY-----\n" # 줄바꿈 문자를 \n으로 대체하여 한 줄로 입력
GCP_CLIENT_EMAIL="your-service-account-email@your-gcp-project-id.iam.gserviceaccount.com"
GCP_CLIENT_ID="your-client-id"
GCP_AUTH_URI="https://accounts.google.com/o/oauth2/auth"
GCP_TOKEN_URI="https://oauth2.googleapis.com/token"
GCP_AUTH_PROVIDER_X509_CERT_URL="https://www.googleapis.com/oauth2/v1/certs"
GCP_CLIENT_X509_CERT_URL="https://www.googleapis.com/robot/v1/metadata/x509/your-service-account-email.iam.gserviceaccount.com"
GCP_UNIVERSE_DOMAIN="googleapis.com"

# Email Configuration (for sending reports)
SMTP_SERVER="smtp.gmail.com" # 예: smtp.gmail.com (Gmail)
SMTP_PORT=587 # 예: 587 (TLS) 또는 465 (SSL)
SENDER_EMAIL="your_sender_email@example.com"
SENDER_PASSWORD="YOUR_EMAIL_APP_PASSWORD" # Gmail의 경우 앱 비밀번호 사용
```

**Google Sheets 권한 설정:**

1.  Google Cloud Platform에서 서비스 계정을 생성하고 JSON 키 파일을 다운로드합니다.
2.  다운로드한 JSON 키 파일에서 `GCP_PRIVATE_KEY` 등의 정보를 추출하여 `.env` 파일에 입력합니다.
3.  서비스 계정 이메일 주소(예: `your-service-account-email@your-gcp-project-id.iam.gserviceaccount.com`)에 Google Sheets 스프레드시트에 대한 **편집자** 권한을 부여해야 합니다.

### 2. 백엔드 설정 및 실행

1.  `backend` 디렉토리로 이동합니다.
    ```bash
    cd backend
    ```
2.  Python 의존성을 설치합니다.
    ```bash
    pip install -r requirements.txt
    ```
3.  FastAPI 애플리케이션을 실행합니다.
    ```bash
    uvicorn app.main:app --reload
    ```
    서버는 기본적으로 `http://127.0.0.1:8000`에서 실행됩니다.

### 3. 프론트엔드 설정 및 실행

1.  `frontend` 디렉토리로 이동합니다.
    ```bash
    cd frontend
    ```
2.  Node.js 의존성을 설치합니다.
    ```bash
    npm install
    ```
3.  프론트엔드 애플리케이션을 실행합니다.
    ```bash
    npm run dev
    ```
    프론트엔드는 기본적으로 `http://localhost:5173`에서 실행됩니다.

### 4. Docker를 이용한 실행 (선택 사항)

프로젝트 루트 디렉토리에서 다음 명령어를 사용하여 Docker Compose로 전체 애플리케이션을 빌드하고 실행할 수 있습니다.

```bash
docker-compose up --build
```

## API 엔드포인트

### 백엔드 (FastAPI)

-   `GET /`: 서버 상태 확인
-   `POST /update-data`: Google Sheets의 원본 데이터를 구조화된 로그 시트로 동기화 (기존 `onEdit` 트리거 대체)
-   `POST /send-report/{report_type}`: 지정된 타입(`week`, `month`, `quarter`, `year`)의 리포트 생성 및 발송
-   `POST /chat`: 챗봇과 상호작용
-   `GET /api/dashboard-data`: 대시보드에 필요한 데이터 제공

### 프론트엔드 (React)

-   `GET /`: 메인 대시보드 페이지

## 기여

기여를 환영합니다! 버그 리포트, 기능 제안 등 언제든지 참여해주세요.

## 라이선스

이 프로젝트는 MIT 라이선스에 따라 배포됩니다.
