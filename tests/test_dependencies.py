"""
의존성 주입 테스트 - 중앙화된 의존성 관리 테스트
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.core.dependencies import get_harbor_agent, get_settings, get_harbor_service
from app.core.agent.harbor_agent import HarborAgent
from app.services.harbor_service import HarborService
from config.settings import Settings

def test_get_settings():
    """Settings 의존성 주입 테스트"""
    settings = get_settings()
    assert isinstance(settings, Settings)

def test_get_harbor_agent_success():
    """정상적으로 에이전트를 가져오는 테스트"""
    app = FastAPI()
    mock_agent = Mock(spec=HarborAgent)
    app.state.harbor_agent = mock_agent
    
    client = TestClient(app)
    
    @app.get("/test")
    def test_endpoint(request):
        agent = get_harbor_agent(request)
        return {"agent_exists": agent is not None}
    
    response = client.get("/test")
    assert response.status_code == 200
    assert response.json()["agent_exists"] is True

def test_get_harbor_agent_not_initialized():
    """에이전트가 초기화되지 않은 경우 테스트"""
    app = FastAPI()
    client = TestClient(app)
    
    @app.get("/test")
    def test_endpoint(request):
        agent = get_harbor_agent(request)
        return {"agent_exists": agent is not None}
    
    response = client.get("/test")
    assert response.status_code == 503
    assert "HarborAgent 서비스를 사용할 수 없습니다" in response.json()["detail"]

def test_get_harbor_service():
    """HarborService 의존성 주입 테스트"""
    mock_agent = Mock(spec=HarborAgent)
    service = get_harbor_service(mock_agent)
    
    assert isinstance(service, HarborService)
    assert service.agent == mock_agent

@pytest.mark.asyncio
async def test_security_with_settings_injection():
    """보안 함수에서 Settings 의존성 주입 테스트"""
    from app.core.security import verify_springboot_request
    
    # Mock Settings 객체
    mock_settings = Mock(spec=Settings)
    mock_settings.INTERNAL_API_KEY = "test-key"
    
    # 올바른 API 키로 테스트
    result = await verify_springboot_request(
        settings=mock_settings,
        x_api_key="test-key"
    )
    assert result is True
    
    # 잘못된 API 키로 테스트
    with pytest.raises(Exception):  # HTTPException 예상
        await verify_springboot_request(
            settings=mock_settings,
            x_api_key="wrong-key"
        )

def test_integration_all_dependencies():
    """모든 의존성이 함께 작동하는 통합 테스트"""
    app = FastAPI()
    
    # Mock objects
    mock_agent = Mock(spec=HarborAgent)
    app.state.harbor_agent = mock_agent
    
    client = TestClient(app)
    
    @app.get("/integration-test")
    def integration_endpoint(request):
        # 모든 의존성 테스트
        settings = get_settings()
        agent = get_harbor_agent(request)
        service = get_harbor_service(agent)
        
        return {
            "settings_loaded": isinstance(settings, Settings),
            "agent_loaded": agent is not None,
            "service_created": isinstance(service, HarborService),
            "dependencies_linked": service.agent == agent
        }
    
    response = client.get("/integration-test")
    assert response.status_code == 200
    
    result = response.json()
    assert result["settings_loaded"] is True
    assert result["agent_loaded"] is True
    assert result["service_created"] is True
    assert result["dependencies_linked"] is True