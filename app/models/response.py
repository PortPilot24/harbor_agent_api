from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class ToolCallInfo(BaseModel):
    """도구 호출 정보 DTO"""
    tool: str = Field(..., description="사용된 도구명")
    arguments: Dict[str, Any] = Field(..., description="도구 호출 인자")
    result: Dict[str, Any] = Field(..., description="도구 실행 결과")

class HarborQueryResponse(BaseModel):
    """항만 질의 응답 DTO"""
    success: bool = Field(..., description="처리 성공 여부")
    answer: str = Field(..., description="AI 에이전트 답변")
    tool_calls: List[ToolCallInfo] = Field(default_factory=list, description="사용된 도구 목록")
    iterations: int = Field(..., description="처리 반복 횟수")
    processing_time: float = Field(..., description="처리 시간(초)")
    timestamp: datetime = Field(default_factory=datetime.now, description="응답 생성 시간")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "answer": "항만 시설 사용료는 선박의 총톤수와 사용 시간에 따라 계산됩니다...",
                "tool_calls": [
                    {
                        "tool": "search_legal_documents",
                        "arguments": {"query": "항만시설 사용료", "n_results": 1},
                        "result": {"message": "1개의 법률 정보를 찾았습니다."}
                    }
                ],
                "iterations": 2,
                "processing_time": 1.5,
                "timestamp": "2024-01-01T12:00:00"
            }
        }

class ErrorResponse(BaseModel):
    """에러 응답 DTO"""
    success: bool = Field(False, description="처리 성공 여부")
    error: str = Field(..., description="에러 메시지")
    error_code: Optional[str] = Field(None, description="에러 코드")
    timestamp: datetime = Field(default_factory=datetime.now, description="에러 발생 시간")

class HealthResponse(BaseModel):
    """헬스 체크 응답 DTO"""
    status: str = Field(..., description="서비스 상태")
    service: str = Field(..., description="서비스명")
    timestamp: datetime = Field(default_factory=datetime.now, description="체크 시간")