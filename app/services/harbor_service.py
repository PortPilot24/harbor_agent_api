from typing import Dict, Any, Optional
import logging

from app.core.agent.harbor_agent import HarborAgent

logger = logging.getLogger(__name__)

class HarborService:
    """항만 관련 비즈니스 로직을 담당하는 서비스"""
    
    def __init__(self, agent: HarborAgent):
        """
        HarborService 초기화
        
        Args:
            agent: HarborAgent 인스턴스 (의존성 주입)
        """
        self.agent = agent
    
    async def process_query(
        self,
        query: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        항만 질의를 처리합니다.
        
        Args:
            query: 사용자 질문
            user_id: 사용자 ID
            session_id: 세션 ID
            context: 추가 컨텍스트
            
        Returns:
            처리 결과 딕셔너리
        """
        try:
            # 컨텍스트가 있으면 질의에 추가
            if context:
                enhanced_query = f"{query}\n\n추가 정보: {context}"
            else:
                enhanced_query = query
            
            # 사용자 정보 로깅
            if user_id:
                logger.info(f"Processing query for user {user_id}: {query[:50]}...")
            
            # 에이전트로 질의 처리
            result = self.agent.process_query(enhanced_query)
            
            logger.info(f"Query processed successfully. Iterations: {result.get('iterations', 'N/A')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in harbor service: {e}")
            raise