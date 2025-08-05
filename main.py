from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.api.v1.harbor import router as harbor_router
from app.core.agent.harbor_agent import HarborAgent
from config.settings import settings

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 에이전트 초기화 (app.state에 저장)
    try:
        logger.info("HarborAgent 초기화 중...")
        app.state.harbor_agent = HarborAgent(
            gemini_api_key=settings.GEMINI_API_KEY,
            db_path=settings.CHROMA_DB_PATH
        )
        logger.info("HarborAgent 초기화 완료")
    except Exception as e:
        logger.error(f"HarborAgent 초기화 실패: {e}")
        raise
    
    yield
    
    # 종료 시 정리 작업
    logger.info("애플리케이션 종료")
    if hasattr(app.state, 'harbor_agent'):
        delattr(app.state, 'harbor_agent')

# FastAPI 애플리케이션 생성
app = FastAPI(
    title="Harbor Agent API",
    description="항만 규정안내 및 상황대응 AI 에이전트 API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 설정 (SpringBoot 서버와의 통신을 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 글로벌 예외 처리
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# 헬스 체크 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "harbor-agent-api"}

# API 라우터 등록
app.include_router(harbor_router, prefix="/api/v1")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )