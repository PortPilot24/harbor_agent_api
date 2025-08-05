from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # API 설정
    DEBUG: bool = False
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    
    # Google Gemini API
    GEMINI_API_KEY: str
    
    # 데이터베이스 경로
    CHROMA_DB_PATH: str = "./data/chroma_db"
    
    # CORS 설정 (SpringBoot 서버 주소)
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:8080",  # SpringBoot 기본 포트
        "http://localhost:3000",  # 개발용
    ]
    
    # SpringBoot 연동 설정
    SPRINGBOOT_BASE_URL: str = "http://localhost:8080"
    API_KEY_HEADER: str = "X-API-Key"
    INTERNAL_API_KEY: str = ""  # SpringBoot와 통신용 내부 API 키
    
    # 로깅 설정
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()