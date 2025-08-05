from pydantic import BaseModel, Field
from typing import Optional

class HarborQueryRequest(BaseModel):
    """항만 질의 요청 DTO"""
    query: str = Field(..., min_length=1, max_length=1000, description="사용자 질문")
    user_id: Optional[str] = Field(None, description="사용자 ID (SpringBoot에서 전달)")
    session_id: Optional[str] = Field(None, description="세션 ID")
    context: Optional[str] = Field(None, description="추가 컨텍스트 정보")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "항만 시설 사용료는 어떻게 계산되나요?",
                "user_id": "user123",
                "session_id": "session456",
                "context": None
            }
        }

class AuthValidationRequest(BaseModel):
    """인증 검증 요청 DTO (SpringBoot 통신용)"""
    token: str = Field(..., description="JWT 토큰")
    endpoint: str = Field(..., description="접근하려는 엔드포인트")