"""
공통 의존성 관리 모듈
"""
from fastapi import HTTPException, Request, Depends
from app.core.agent.harbor_agent import HarborAgent
from app.services.harbor_service import HarborService
from config.settings import Settings

def get_settings() -> Settings:
    """
    Settings 객체를 반환합니다.
    테스트 시 설정을 동적으로 변경할 수 있도록 의존성 주입으로 관리합니다.
    
    Returns:
        Settings 인스턴스
    """
    return Settings()

def get_harbor_agent(request: Request) -> HarborAgent:
    """
    FastAPI app.state에서 HarborAgent 인스턴스를 가져옵니다.
    
    Args:
        request: FastAPI Request 객체
        
    Returns:
        HarborAgent 인스턴스
        
    Raises:
        HTTPException: 에이전트가 초기화되지 않은 경우
    """
    if not hasattr(request.app.state, 'harbor_agent'):
        raise HTTPException(
            status_code=503,
            detail="HarborAgent 서비스를 사용할 수 없습니다. 관리자에게 문의하세요."
        )
    return request.app.state.harbor_agent

def get_harbor_service(agent: HarborAgent = Depends(get_harbor_agent)) -> HarborService:
    """
    HarborService 의존성 주입
    
    Args:
        agent: HarborAgent 인스턴스 (의존성 주입)
        
    Returns:
        HarborService 인스턴스
    """
    return HarborService(agent)