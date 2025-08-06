import chromadb
import json
import sqlite3
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import logging
import google.generativeai as genai
import os
import re
import time

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """검색 결과를 담는 데이터 클래스"""
    content: str
    metadata: Dict
    distance: float

class GeminiClient:
    """무료 Gemini API 클라이언트"""
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash-lite')
        self.generation_config = genai.types.GenerationConfig(
            temperature=0.1, max_output_tokens=2048, top_p=0.9, top_k=40
        )

    def generate_response(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        """단일 JSON 객체 응답을 파싱하는 최종 간소화 버전"""
        try:
            formatted_prompt = self._format_messages_for_gemini(messages)
            if tools:
                tool_descriptions = self._format_tools_for_prompt(tools)
                formatted_prompt += f"\n\n# 사용 가능한 도구 목록:\n{tool_descriptions}\n\n"
                formatted_prompt += """
# 지시사항:
- 만약 사용자의 질문에 답변하기 위해 도구를 사용해야 한다면, 반드시 다음 JSON 형식에 맞춰 단 하나의 JSON 객체만 생성해야 합니다. 다른 텍스트는 일절 포함하지 마세요.
{
  "reasoning": "왜 이 도구들을 선택했는지에 대한 간단한 생각.",
  "tool_calls": [
    {
      "function_name": "호출할 도구명",
      "arguments": {"매개변수": "값"}
    }
  ]
}

- 만약 도구를 사용할 필요가 없다면, 반드시 다음 JSON 형식에 맞춰 단 하나의 JSON 객체만 생성해야 합니다.
{
  "reasoning": "답변에 대한 간단한 생각.",
  "content": "사용자에게 보여줄 최종 답변 내용."
}
"""
            token_count = self.model.count_tokens(formatted_prompt)
            print("--- [API 요청 전 확인] ---")
            print(f"▶ 전송될 프롬프트 내용: \n{formatted_prompt}")
            print(f"▶ 총 토큰 수: {token_count.total_tokens} 개")
            print("--------------------------")

            response = self.model.generate_content(
                formatted_prompt, generation_config=self.generation_config
            )
            response_text = response.text.strip()

            try:
                match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if not match:
                    return {"type": "text", "content": response_text}

                json_str = match.group(0)
                parsed_response = json.loads(json_str, strict=False)

                if "tool_calls" in parsed_response and parsed_response["tool_calls"]:
                    return {"type": "tool_call_list", "calls": parsed_response["tool_calls"]}
                elif "content" in parsed_response:
                    return {"type": "text", "content": parsed_response["content"]}
                else:
                    return {"type": "text", "content": response_text}
            except json.JSONDecodeError:
                return {"type": "text", "content": response_text}
        except Exception as e:
            logger.error(f"Gemini API 오류: {e}")
            # 429 Rate Limit 오류 처리
            if "429" in str(e):
                return {"type": "error", "content": "API 요청 한도를 초과했습니다. 1분 후에 다시 시도해주세요."}
            return {"type": "error", "content": "죄송합니다. 현재 응답을 생성할 수 없습니다."}

    def _format_messages_for_gemini(self, messages: List[Dict]) -> str:
        formatted = ""
        for msg in messages:
            role, content = msg.get("role", ""), msg.get("content", "")
            if role == "system": formatted += f"# 시스템 지시사항:\n{content}\n\n"
            elif role == "user": formatted += f"# 사용자 질문:\n{content}\n\n"
            elif role == "assistant": formatted += f"# 이전 답변:\n{content}\n\n"
            elif role == "tool": formatted += f"# 도구 실행 결과:\n{content}\n\n"
        return formatted

    def _format_tools_for_prompt(self, tools: List[Dict]) -> str:
        tool_descriptions = []
        for tool in tools:
            func = tool.get("function", {})
            name, description = func.get("name", ""), func.get("description", "")
            parameters = func.get("parameters", {}).get("properties", {})
            param_desc = [f"  - {p_name} ({p_info.get('type', '')}): {p_info.get('description', '')}" for p_name, p_info in parameters.items()]
            tool_descriptions.append(f"• {name}: {description}\n" + "\n".join(param_desc))
        return "\n\n".join(tool_descriptions)

class ChromaDBManager:
    """ChromaDB 관리 클래스"""
    def __init__(self, db_path: str = "./chroma_db"):  # 🔄 경로 수정
        self.client = chromadb.PersistentClient(path=db_path)
        self.legal_collection = None
        self.manual_collection = None
        try:
            self.legal_collection = self.client.get_collection(name="legal_docs")
            self.manual_collection = self.client.get_collection(name="legal_manuals")
            logger.info("ChromaDB 컬렉션 연결 성공")
        except Exception as e:
            logger.error(f"ChromaDB 연결 실패: {e}")

    def search_legal(self, query: str, n_results: int = 3, where_filter: Optional[Dict] = None) -> List[SearchResult]:
        if not self.legal_collection: return []
        try:
            results = self.legal_collection.query(query_texts=[query], n_results=n_results, where=where_filter)
            return [SearchResult(content=d, metadata=m, distance=dist) for d, m, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0])]
        except Exception as e:
            logger.error(f"법률 문서 검색 오류: {e}")
            return []

    def search_manual(self, query: str, n_results: int = 3, where_filter: Optional[Dict] = None) -> List[SearchResult]:
        if not self.manual_collection: return []
        try:
            results = self.manual_collection.query(query_texts=[query], n_results=n_results, where=where_filter)
            return [SearchResult(content=d, metadata=m, distance=dist) for d, m, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0])]
        except Exception as e:
            logger.error(f"매뉴얼 검색 오류: {e}")
            return []

class HarborAgentTools:
    """Harbor Agent가 사용할 수 있는 도구들"""
    def __init__(self, db_manager: ChromaDBManager):
        self.db_manager = db_manager

    @staticmethod
    def get_tool_definitions() -> List[Dict]:
        return [
            {"type": "function", "function": {"name": "search_legal_documents", "description": "항만 관련 법률, 규정, 조문을 검색합니다.", "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "검색할 법률 내용"}, "structure_filter": {"type": "string", "description": "문서 구조 필터(article, chapter 등)"}, "n_results": {"type": "integer", "description": "검색 결과 개수(1-3)"}}, "required": ["query"]}}},
            {"type": "function", "function": {"name": "search_manual_documents", "description": "항만 업무 절차, 안전 매뉴얼, 실무 가이드를 검색합니다.", "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "검색할 절차나 방법"}, "n_results": {"type": "integer", "description": "검색 결과 개수(1-3)"}}, "required": ["query"]}}},
        ]

    def execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        try:
            if tool_name == "search_legal_documents": return self._search_legal_documents(**arguments)
            elif tool_name == "search_manual_documents": return self._search_manual_documents(**arguments)
            else: return {"error": f"알 수 없는 도구: {tool_name}"}
        except Exception as e:
            logger.error(f"도구 실행 오류 {tool_name}: {e}")
            return {"error": f"도구 실행 중 오류 발생: {str(e)}"}

    def _format_search_results(self, results: List[SearchResult]) -> List[Dict]:
        if not results: return []
        return [{"content": r.content, "source_file": r.metadata.get('source_file', '알 수 없음')} for r in results]

    def _search_legal_documents(self, query: str, structure_filter: str = "", n_results: int = 2) -> Dict:
        where_filter = {"structure_type": structure_filter} if structure_filter else None
        results = self.db_manager.search_legal(query, n_results, where_filter)
        if not results: return {"message": "관련 법률 정보를 찾을 수 없습니다.", "results": []}
        return {"message": f"{len(results)}개의 법률 정보를 찾았습니다.", "results": self._format_search_results(results)}

    def _search_manual_documents(self, query: str, n_results: int = 2) -> Dict:
        results = self.db_manager.search_manual(query, n_results)
        if not results: return {"message": "관련 매뉴얼 정보를 찾을 수 없습니다.", "results": []}
        return {"message": f"{len(results)}개의 매뉴얼 정보를 찾았습니다.", "results": self._format_search_results(results)}

class HarborAgent:
    """항만 규정안내 및 상황대응 Agent"""
    def __init__(self, api_key: str, db_path: str = "./chroma_db"):  # 🔄 매개변수명 변경 및 경로 수정
        self.gemini = GeminiClient(api_key)  # 🔄 매개변수명 변경
        self.db_manager = ChromaDBManager(db_path)
        self.tools = HarborAgentTools(self.db_manager)
        self.conversation_history = []

    def _create_system_prompt(self) -> str:
        return """당신은 대한민국 항만 관련 전문 AI Assistant입니다. 당신의 임무는 사용자의 질문을 이해하고, '사용 가능한 도구'를 사용하여 정보를 찾은 뒤, 그 결과를 종합하여 완전한 답변을 제공하는 것입니다.

    # 답변 규칙
    1. 최우선적으로 '도구'를 통해 찾은 정보를 기반으로 답변을 생성해야 합니다.
    2. 만일 도구로 찾은 정보가 질문에 답하기에 부족하거나 관련이 없다면, "제공된 문서에서는 관련 정보를 찾을 수 없었습니다."라고 명시적으로 밝히세요.
    3. 만일 도구로 찾은 정보가 질문에 답하기에 부족하거나 관련이 없다면, 참고용으로 당신의 일반 지식에 기반하여 인터넷에서 검색해본 후 답변을 추가로 제공할 수 있습니다.

    항상 정해진 JSON 형식으로만 응답해야 합니다."""
    
    def process_query(self, query: str) -> Dict:
        """
        다중 Tool Call을 순차적으로 실행하며, 최대 반복 횟수 도달 시 강제로 최종 답변을 생성하는 버전
        """
        try:
            self.conversation_history.append({"role": "user", "content": query})
            messages = [{"role": "system", "content": self._create_system_prompt()}] + self.conversation_history
            tools = HarborAgentTools.get_tool_definitions()
            
            # API 요청 횟수를 2회로 제한 (최초 1회 + 추가 정보 요청 1회)
            max_iterations = 2 
            iteration = 0
            tool_results_log = []

            while iteration < max_iterations:
                iteration += 1
                logger.info(f"--- [Agent 반복 {iteration}/{max_iterations}] ---")
                response = self.gemini.generate_response(messages, tools)

                if response["type"] == "tool_call_list":
                    # 모델이 도구 사용을 요청한 경우
                    for tool_call in response["calls"]:
                        function_name, arguments = tool_call["function_name"], tool_call.get("arguments", {})
                        logger.info(f"도구 호출: {function_name} with {arguments}")
                        
                        # 도구 실행
                        tool_result = self.tools.execute_tool(function_name, arguments)
                        tool_results_log.append({"tool": function_name, "arguments": arguments, "result": tool_result})
                        
                        # 도구 실행 결과를 대화 내역에 추가
                        messages.append({"role": "tool", "content": f"도구 '{function_name}' 실행 결과: {json.dumps(tool_result, ensure_ascii=False)}"})
                    
                    # 다음 반복을 위해 계속 진행
                    continue

                elif response["type"] == "text":
                    # 모델이 도구 없이 바로 답변을 생성한 경우
                    self.conversation_history.append({"role": "assistant", "content": response["content"]})
                    return {"answer": response["content"], "tool_calls": tool_results_log, "iterations": iteration}

                else: # "error"
                    return {"answer": response.get("content", "오류가 발생했습니다."), "tool_calls": tool_results_log, "iterations": iteration}

            # --- ✨ 핵심 수정 부분 시작 ✨ ---
            # 최대 반복 횟수에 도달한 경우, 강제로 답변 생성
            logger.info(f"최대 반복 횟수({max_iterations}회)에 도달했습니다. 현재까지 수집된 정보로 최종 답변을 생성합니다.")
            
            # 최종 답변을 생성하라는 지시를 추가
            final_instruction = "지금까지의 도구 실행 결과를 모두 종합하여 사용자의 최초 질문에 대한 최종 답변을 'content' 필드에 담아 JSON 형식으로 작성해주세요. 더 이상 도구를 호출할 수 없습니다. 만약 정보가 부족하다면, 현재까지 확인된 내용과 직접 탐색한 정보를 바탕으로 답변해야 합니다."
            messages.append({"role": "user", "content": final_instruction})
            
            # 'tools=None'으로 설정하여 더 이상 도구를 사용하지 못하도록 하고 API 호출
            final_response = self.gemini.generate_response(messages, tools=None)
            
            if final_response["type"] == "text":
                final_answer = final_response["content"]
            else:
                # 마지막 호출에서도 오류가 발생하거나 텍스트 답변이 없는 경우
                final_answer = "최종 답변을 생성하는 데 실패했습니다. 수집된 정보는 다음과 같습니다."

            self.conversation_history.append({"role": "assistant", "content": final_answer})
            return {"answer": final_answer, "tool_calls": tool_results_log, "iterations": iteration}
            # --- ✨ 핵심 수정 부분 끝 ✨ ---

        except Exception as e:
            logger.error(f"process_query 처리 중 심각한 오류 발생: {e}", exc_info=True)
            return {"answer": "시스템 오류가 발생했습니다.", "tool_calls": [], "iterations": 0}
