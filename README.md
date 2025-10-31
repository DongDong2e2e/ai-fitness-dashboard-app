# AI Fitness Dashboard App

## 프로젝트 개요

이 프로젝트는 Google Sheets와 Google Apps Script(GAS)로 구현되었던 운동 기록 관리 및 AI 리포트 자동 생성 서비스를 현대적인 웹 스택으로 마이그레이션한 애플리케이션입니다. 사용자의 운동 기록을 데이터베이스화하고, Gemini AI를 활용하여 주간/월간/분기/연간 맞춤형 리포트를 생성하여 이메일로 발송합니다. 또한, 대시보드와 챗봇 기능을 통해 운동 데이터를 시각적으로 확인하고 AI와 상호작용할 수 있습니다.

## 주요 기능

- **운동 기록 관리:** PostgreSQL 데이터베이스에 운동 데이터를 구조화하여 저장하고 관리합니다.
- **AI 기반 리포트:** Gemini AI를 활용하여 개인화된 운동 분석 리포트(주간, 월간, 분기, 연간)를 생성하고 지정된 이메일로 자동 발송합니다.
- **맞춤형 운동 루틴 제안:** AI 분석을 기반으로 사용자에게 최적화된 운동 루틴을 추천합니다.
- **대시보드:** 운동 볼륨, 최고 기록, 인바디 변화 등 핵심 데이터를 시각적으로 제공합니다.
- **챗봇:** 운동 기록 및 인바디 데이터에 대해 자연어로 질문하고 답변을 받을 수 있습니다. (예: "이번 주 벤치프레스 최고 기록 보여줘", "최근 인바디 결과 알려줘", "스쿼트 중량 변화를 그래프로 그려줘")

## 기술 스택

- **백엔드:** Python, FastAPI
- **프론트엔드:** React (JavaScript)
- **데이터베이스:** PostgreSQL
- **AI:** Google Gemini API
- **배포:** Docker, Docker Compose

## 프로젝트 설정 및 실행

프로젝트를 로컬에서 실행하기 위한 단계별 가이드입니다.

### 1. 환경 변수 설정

`backend` 디렉토리에 있는 `.env.example` 파일을 `.env` 파일로 복사한 후, 자신의 환경에 맞게 값을 수정해주세요. 이 파일은 민감한 정보(API 키, 비밀번호 등)를 관리합니다.

```bash
cp backend/.env.example backend/.env
```

이후 `backend/.env` 파일을 열어 각 변수에 해당하는 값을 입력합니다.

### 2. Docker를 이용한 전체 서비스 실행

프로젝트 루트 디렉토리에서 다음 명령어를 사용하여 Docker Compose로 전체 애플리케이션을 빌드하고 실행합니다.

```bash
docker-compose up --build
```

- 백엔드 서버: `http://localhost:8000`
- 프론트엔드: `http://localhost:5173` (Vite 기본 포트)

### 3. 데이터 마이그레이션 (최초 1회 실행)

애플리케이션이 처음 실행되면 데이터베이스는 비어있습니다. 기존 Google Sheets의 데이터를 PostgreSQL 데이터베이스로 옮기려면 다음 단계를 따르세요.

1.  웹 브라우저나 API 테스트 도구(예: Postman)를 사용하여 아래 엔드포인트로 `POST` 요청을 보냅니다.
    ```
    http://localhost:8000/api/migrate-data
    ```
2.  요청이 성공하면 Google Sheets의 모든 데이터가 PostgreSQL 데이터베이스로 복사됩니다. 이 작업은 한 번만 수행하면 됩니다.

### 4. (선택) 개별 서비스 실행

Docker를 사용하지 않고 각 서비스를 직접 실행할 수도 있습니다.

**백엔드 (FastAPI):**
```bash
cd backend
# .env 파일 설정 확인
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**프론트엔드 (React):**
```bash
cd frontend
npm install
npm run dev
```

## API 엔드포인트

-   `GET /`: 서버 상태 확인
-   `POST /api/migrate-data-from-csv`: 로컬 CSV 데이터를 PostgreSQL로 마이그레이션
-   `GET /api/dashboard-data`: 대시보드에 필요한 데이터 제공
-   `POST /api/workout-logs`: 새로운 운동 기록 추가
-   `POST /api/inbody-records`: 새로운 인바디 기록 추가
-   `POST /send-report/{report_type}`: 리포트 생성 및 발송
-   `POST /chat`: 챗봇과 상호작용
