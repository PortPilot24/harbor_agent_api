# 1. Python 기반 이미지 사용
FROM python:3.11-slim
# 2. 작업 디렉토리 생성
WORKDIR /app
# 3. 의존성 파일 복사
COPY requirements.txt .
# 4. 필수 패키지 설치 (pip 최신화 포함)
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt
# 5. 소스 코드 복사
COPY . .
# Hugging Face 모델 복사
COPY ko-sroberta-multitask /app/models/ko-sroberta-multitask
# 환경 변수 (선택 사항, Embedding 경로 지정)
ENV HF_MODEL_PATH=/app/models/ko-sroberta-multitask
# 6. 포트 개방
EXPOSE 8000
# 7. 컨테이너 실행 명령
# run.py 내부에서 uvicorn을 실행하므로 python run.py 사용
CMD ["python", "run.py"]