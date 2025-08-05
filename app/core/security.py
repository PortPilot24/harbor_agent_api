from fastapi import HTTPException, Header, Depends
from typing import Optional
import httpx
import logging

from config.settings import Settings
from app.core.dependencies import get_settings

logger = logging.getLogger(__name__)

async def verify_springboot_request(
    settings: Settings = Depends(get_settings),  # ✅ 의존성 주입으로 Settings 주입
    x_api_key: Optional[str] = Header(None),
    authorization: Optional[str] = Header(None)
):
    """
    SpringBoot에서 전달된 요청을 검증합니다.
    필요시 SpringBoot 서버에 토큰 검증을 요청할 수 있습니다.
    """
    
    # 내부 API 키 검증 (SpringBoot ↔ FastAPI 간 통신)
    if settings.INTERNAL_API_KEY and x_api_key != settings.INTERNAL_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    
    # JWT 토큰이 있으면 SpringBoot에 검증 요청 (선택사항)
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        is_valid = await validate_token_with_springboot(token, settings)
        if not is_valid:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
    
    return True

async def validate_token_with_springboot(token: str, settings: Settings) -> bool:
    """
    SpringBoot 서버에 토큰 검증을 요청합니다.
    
    Args:
        token: JWT 토큰
        settings: Settings 객체 (의존성 주입)
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.SPRINGBOOT_BASE_URL}/api/auth/validate",
                headers={"Authorization": f"Bearer {token}"},
                timeout=5.0
            )
            return response.status_code == 200
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        return False