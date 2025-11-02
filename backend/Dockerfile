# 1. 어떤 OS와 Python 버전으로 시작할지 선택 (가벼운 버전)
FROM python:3.12-slim

# 2. 컨테이너 안에서 작업할 기본 폴더 설정
WORKDIR /app

# 3. 필요한 라이브러리 목록 파일을 먼저 복사 (매우 중요한 최적화 단계)
COPY requirements.txt .

# 4. 라이브러리 설치
RUN pip install --no-cache-dir -r requirements.txt

# 5. 우리 소스 코드 전체를 컨테이너 안으로 복사
COPY ./app /app

# 6. 이 컨테이너는 외부와 8000번 포트로 통신할 것임을 알림
EXPOSE 8000

# 7. 컨테이너가 시작될 때 실행할 최종 명령어 (FastAPI 서버 실행)
# 0.0.0.0으로 해야 컨테이너 외부에서 접속 가능
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]