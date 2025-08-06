from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
from contextlib import asynccontextmanager

# 로컬 import (같은 디렉토리의 다른 파일들)
from models import QueryRequest, QueryResponse, HealthResponse
from harbor_agent import HarborAgent

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 전역 agent 변수
agent = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """앱 시작/종료 시 실행되는 함수"""
    global agent
    
    # 시작 시 - Agent 초기화
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        logger.error("GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
        raise RuntimeError("GEMINI_API_KEY is required")
    
    try:
        agent = HarborAgent(api_key)
        logger.info("HarborAgent 초기화 완료")
    except Exception as e:
        logger.error(f"HarborAgent 초기화 실패: {e}")
        raise
    
    yield
    
    # 종료 시 - 정리 작업 (필요한 경우)
    logger.info("서버 종료")

# FastAPI 앱 생성
app = FastAPI(
    title="Harbor Agent API",
    description="항만 규정안내 및 상황대응 Agent API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포시에는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_model=Dict[str, str])
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Harbor Agent API", 
        "status": "running",
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """헬스 체크 엔드포인트"""
    global agent
    
    agent_status = "ready" if agent is not None else "not_initialized"
    
    return HealthResponse(
        status="healthy",
        agent_status=agent_status,
        api_version="1.0.0"
    )

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """쿼리 처리 엔드포인트"""
    global agent
    
    if agent is None:
        raise HTTPException(
            status_code=503, 
            detail="Agent가 초기화되지 않았습니다."
        )
    
    if not request.query.strip():
        raise HTTPException(
            status_code=400, 
            detail="쿼리가 비어있습니다."
        )
    
    try:
        logger.info(f"쿼리 처리 시작: {request.query[:50]}...")
        
        # Agent로 쿼리 처리
        result = agent.process_query(request.query)
        
        response = QueryResponse(
            answer=result['answer'],
            query=request.query,
            tool_calls=result.get('tool_calls', []),
            iterations=result.get('iterations', 1),
            success=True
        )
        
        logger.info(f"쿼리 처리 완료: {response.iterations}회 반복")
        return response
        
    except Exception as e:
        logger.error(f"쿼리 처리 오류: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"쿼리 처리 중 오류가 발생했습니다: {str(e)}"
        )

@app.get("/status")
async def get_status():
    """서버 상태 정보"""
    global agent
    
    return {
        "server": "running",
        "agent_initialized": agent is not None,
        "endpoints": [
            {"path": "/", "method": "GET", "description": "루트"},
            {"path": "/health", "method": "GET", "description": "헬스 체크"},
            {"path": "/query", "method": "POST", "description": "쿼리 처리"},
            {"path": "/status", "method": "GET", "description": "상태 정보"},
            {"path": "/docs", "method": "GET", "description": "API 문서"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    
    # 환경변수에서 포트 설정 (기본값: 8000)
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"서버 시작: {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,  # 개발 모드
        log_level="info"
    )