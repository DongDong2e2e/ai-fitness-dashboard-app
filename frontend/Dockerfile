# --- 1단계: 빌드(Build) 환경 ---
# 무거운 Node.js 환경을 'builder'라는 별명으로 사용
FROM node:20 as builder

# 작업 폴더 설정
WORKDIR /app

# 라이브러리 목록 파일 먼저 복사 (캐싱 최적화)
COPY package*.json ./

# 라이브러리 설치
RUN npm install

# 소스 코드 전체 복사
COPY . .

# React 앱을 순수 HTML/CSS/JS 파일로 변환 (빌드)
RUN npm run build

# --- 2단계: 최종 실행(Production) 환경 ---
# 매우 가벼운 Nginx 웹서버로 시작
FROM nginx:stable-alpine

# 1단계(builder)에서 생성된 빌드 결과물(dist 폴더)만 복사해옴
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx는 기본적으로 80번 포트를 사용
EXPOSE 80

# 컨테이너 시작 시 Nginx 서버 실행
CMD ["nginx", "-g", "daemon off;"]