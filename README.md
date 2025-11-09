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

- **백엔드:** Python 3.12, FastAPI
- **프론트엔드:** React (JavaScript)
- **데이터베이스:** PostgreSQL
- **AI:** Google Gemini API
- **배포:** Docker, Docker Compose

## 프로젝트 설정 및 실행

프로젝트를 로컬에서 실행하기 위한 단계별 가이드입니다.

### 1. Python 버전 설정 (권장)

이 프로젝트는 Python 3.12에서 개발되었습니다. `pyenv`를 사용하여 로컬 파이썬 버전을 설정하는 것을 권장합니다.

```bash
# pyenv가 설치되어 있지 않다면 설치
brew install pyenv

# pyenv 초기화 (사용하는 쉘에 맞게 .zshrc 또는 .bashrc 등 수정)
echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init --path)"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
source ~/.zshrc

# Python 3.12.0 설치 및 로컬 버전 설정
pyenv install 3.12.0
pyenv local 3.12.0
```

### 2. 환경 변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고, `backend/.env.example` 파일의 내용을 복사하여 자신의 환경에 맞게 값을 수정해주세요. 이 파일은 민감한 정보(API 키, 비밀번호 등)를 관리합니다.

```bash
cp backend/.env.example .env
```

이후 `.env` 파일을 열어 각 변수에 해당하는 값을 입력합니다. 특히 `SECRET_KEY`는 반드시 안전한 값으로 변경해야 합니다.

### 3. Docker를 이용한 전체 서비스 실행

프로젝트 루트 디렉토리에서 다음 명령어를 사용하여 Docker Compose로 전체 애플리케이션을 빌드하고 실행합니다.

```bash
docker-compose up --build -d
```
`-d` 플래그는 백그라운드에서 서비스를 실행합니다.

- 백엔드 서버: `http://localhost:8000`
- 프론트엔드: `http://localhost:3000`

### 4. 데이터베이스 마이그레이션

애플리케이션이 처음 실행되면 데이터베이스 스키마를 생성해야 합니다. 다음 명령어를 실행하여 데이터베이스를 최신 상태로 업데이트합니다.

```bash
docker-compose exec backend alembic upgrade head
```
`models.py`의 내용이 변경될 때마다 이 명령어를 다시 실행하여 데이터베이스 스키마를 업데이트해야 합니다.

### 5. 사용자 생성 및 데이터 임포트

#### 5.1. 사용자 생성 (회원가입)
API를 사용하기 위해 먼저 사용자를 생성해야 합니다. 웹 브라우저나 API 테스트 도구(예: Postman)를 사용하여 아래 엔드포인트로 `POST` 요청을 보냅니다.

- **URL:** `http://localhost:8000/api/v1/auth/users`
- **Body (JSON):**
  ```json
  {
    "email": "test@example.com",
    "password": "your_password"
  }
  ```

#### 5.2. 로그인 (토큰 발급)
사용자를 생성한 후, 로그인을 통해 API 요청에 필요한 `access_token`을 발급받습니다.

- **URL:** `http://localhost:8000/api/v1/auth/token`
- **Body (form-data):**
  - `username`: `test@example.com`
  - `password`: `your_password`

요청이 성공하면 `access_token`이 포함된 응답을 받게 됩니다.

#### 5.3. (선택) CSV 데이터 임포트
`/backend/data` 폴더에 제공된 CSV 파일들을 현재 로그인된 사용자의 데이터로 가져올 수 있습니다.

- **URL:** `http://localhost:8000/api/v1/migrate-data-from-csv`
- **Method:** `POST`
- **Headers:** `Authorization: Bearer <your_access_token>`

### 6. 테스트 실행

백엔드 테스트를 실행하여 모든 것이 정상적으로 동작하는지 확인할 수 있습니다.

```bash
# backend 디렉토리에서 실행
cd backend

# 의존성 설치
pip install -r requirements.txt

# 테스트 실행
python -m pytest
```

## API 엔드포인트

-   `GET /`: 서버 상태 확인

#### 인증 (Auth)
-   `POST /api/v1/auth/users`: 신규 사용자 생성 (회원가입)
-   `POST /api/v1/auth/token`: 로그인 및 액세스 토큰 발급
-   `GET /api/v1/auth/users/me`: 현재 로그인된 사용자 정보 확인 (🔒 Auth Required)

#### 데이터 관리 (🔒 Auth Required)
-   `POST /api/v1/migrate-data-from-csv`: 로컬 CSV 데이터를 현재 사용자의 데이터로 마이그레이션
-   `GET /api/v1/dashboard-data`: 대시보드에 필요한 데이터 제공
-   `POST /api/v1/exercises`: 새로운 운동 정보 추가 (현재는 인증 없이 사용 가능)
-   `GET /api/v1/workout-logs`: 현재 사용자의 운동 기록 조회
-   `POST /api/v1/workout-logs`: 새로운 운동 기록 추가
-   `GET /api/v1/inbody-records`: 현재 사용자의 인바디 기록 조회
-   `POST /api/v1/inbody-records`: 새로운 인바디 기록 추가
-   `POST /api/v1/send-report/{report_type}`: 리포트 생성 및 발송
-   `POST /api/v1/chat`: 챗봇과 상호작용
