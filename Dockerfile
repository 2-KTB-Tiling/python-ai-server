# 1. 경량 Python 이미지 사용
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 필수 패키지 설치 (OS-level dependencies)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 4. 필요한 Python 패키지 설치
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt

# 5. 애플리케이션 코드 복사
COPY . /app

# 6. 환경 변수 설정 (Jenkins에서 전달받음)
ENV PYTHONUNBUFFERED=1

# 7. FastAPI 실행 (환경 변수를 사용하여 실행)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
