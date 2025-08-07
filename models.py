from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class QueryRequest(BaseModel):
    """쿼리 요청 모델"""
    query: str = Field(..., description="처리할 쿼리", min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "컨테이너 하역 시 안전 규정에 대해 알려주세요"
            }
        }

class ToolCall(BaseModel):
    tool: str
    source_file: Optional[str] = None

# 최종 응답을 위한 모델
class QueryResponse(BaseModel):
    answer: str
    query: str
    tool_calls: List[ToolCall]
    iterations: int
    success: bool
    
# class ToolCall(BaseModel):
#     """도구 호출 정보 모델"""
#     tool: str = Field(..., description="사용된 도구명")
#     arguments: Optional[Dict[str, Any]] = Field(None, description="도구 인자")
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "tool": "regulation_search",
#                 "arguments": {"keyword": "안전규정"}
#             }
#         }

# class QueryResponse(BaseModel):
#     """쿼리 응답 모델"""
#     answer: str = Field(..., description="Agent의 답변")
#     query: str = Field(..., description="원본 쿼리")
#     tool_calls: List[ToolCall] = Field(default_factory=list, description="사용된 도구들")
#     iterations: int = Field(default=1, description="처리 반복 횟수")
#     success: bool = Field(default=True, description="처리 성공 여부")
    
#     class Config:
#         json_schema_extra = {
#             "example": {
#                 "answer": "컨테이너 하역 시에는 다음과 같은 안전 규정을 준수해야 합니다...",
#                 "query": "컨테이너 하역 시 안전 규정에 대해 알려주세요",
#                 "tool_calls": [
#                     {
#                         "tool": "regulation_search",
#                         "arguments": {"keyword": "안전규정"}
#                     }
#                 ],
#                 "iterations": 2,
#                 "success": True
#             }
#         }

class HealthResponse(BaseModel):
    """헬스 체크 응답 모델"""
    status: str = Field(..., description="서버 상태")
    agent_status: str = Field(..., description="Agent 상태")
    api_version: str = Field(..., description="API 버전")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "agent_status": "ready",
                "api_version": "1.0.0"
            }
        }

class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    detail: str = Field(..., description="에러 상세 정보")
    error_code: Optional[str] = Field(None, description="에러 코드")
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "쿼리 처리 중 오류가 발생했습니다",
                "error_code": "QUERY_PROCESSING_ERROR"
            }
        }