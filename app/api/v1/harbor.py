from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional
import time
import logging

from app.models.request import HarborQueryRequest
from app.models.response import HarborQueryResponse, ErrorResponse
from app.services.harbor_service import HarborService
from app.core.security import verify_springboot_request
# ✅ 중앙 의존성 모듈에서 모든 의존성 함수를 가져옵니다
from app.core.dependencies import get_harbor_service, get_harbor_agent

logger = logging.getLogger(__name__)

# 라우터 생성 (보안 의존성 적용)
router = APIRouter(
    prefix="/harbor", 
    tags=["harbor"],
    dependencies=[Depends(verify_springboot_request)]  # 모든 엔드포인트에 보안 적용
)

@router.post("/query", response_model=HarborQueryResponse)
async def process_harbor_query(
    request: HarborQueryRequest,
    harbor_service: HarborService = Depends(get_harbor_service),  # ✅ 중앙화된 의존성 사용
    x_forwarded_user: Optional[str] = Header(None),  # SpringBoot에서 전달하는 사용자 정보
    x_forwarded_roles: Optional[str] = Header(None),  # SpringBoot에서 전달하는 권한 정보
):
    """
    항만 관련 질의를 처리합니다.
    
    - **query**: 사용자의 질문
    - **user_id**: 사용자 ID (선택사항)
    - **session_id**: 세션 ID (선택사항)
    - **context**: 추가 컨텍스트 (선택사항)
    """
    try:
        start_time = time.time()
        
        # SpringBoot에서 전달된 사용자 정보 로깅
        if x_forwarded_user:
            logger.info(f"Request from user: {x_forwarded_user}, roles: {x_forwarded_roles}")
        
        # 질의 처리
        result = await harbor_service.process_query(
            query=request.query,
            user_id=request.user_id or x_forwarded_user,
            session_id=request.session_id,
            context=request.context
        )
        
        processing_time = time.time() - start_time
        
        return HarborQueryResponse(
            success=True,
            answer=result["answer"],
            tool_calls=result.get("tool_calls", []),
            iterations=result.get("iterations", 1),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"Query processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"질의 처리 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/status")
async def get_agent_status(
    agent = Depends(get_harbor_agent)  # ✅ 중앙화된 의존성 사용
):
    """에이전트 상태 확인"""
    try:
        return {
            "status": "active",
            "agent_initialized": agent is not None,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": time.time()
        }