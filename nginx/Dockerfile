FROM nginx:latest

# 기존 설정 파일 제거 (필요한 경우)
RUN rm /etc/nginx/conf.d/default.conf

# 새 설정 파일 복사
COPY nginx.conf /etc/nginx/conf.d/