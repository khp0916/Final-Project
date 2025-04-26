# services/llm.py
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)
load_dotenv()

# API 키 확인
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

genai.configure(api_key=api_key)

async def create_product_explanation(query: str, products: List[Dict[str, Any]]) -> str:
    """
    제품 검색 결과에 대한 설명을 생성합니다.
    
    Args:
        query: 사용자 검색어
        products: 검색된 제품 목록
    """
    try:
        # 제품 정보를 JSON 형식으로 변환
        products_info = json.dumps(products, ensure_ascii=False, indent=2)
        
        # 프롬프트 구성
        prompt = f"""
        사용자가 '{query}'로 제품을 검색했습니다.
        다음 제품들이 검색되었습니다:
        
        {products_info}
        
        지시사항:
        1. 각 제품의 주요 특징을 간단명료하게 설명해주세요.
        2. 사용자의 검색어와 각 제품의 관련성을 설명해주세요.
        3. 유사도 점수를 참고하여 가장 관련성 높은 제품부터 설명해주세요.
        4. 전문적인 용어는 일반 사용자가 이해하기 쉽게 설명해주세요.
        5. 각 제품 설명은 2-3문장으로 간결하게 작성해주세요.
        
        답변 형식:
        - [제품명]: [주요 특징과 검색어와의 관련성 설명]
        """
        
        # Gemini API 호출
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Error in create_product_explanation: {str(e)}")
        return "제품 설명을 생성하는 중 오류가 발생했습니다."

async def create_answer_with_gemini(query: str, retrieved_docs: List[Dict[str, str]], chat_history: List[Dict[str, str]] = None) -> str:
    """
    RAG를 활용하여 Gemini API를 통해 응답을 생성합니다.
    
    Args:
        query: 사용자 질문
        retrieved_docs: 벡터 DB에서 검색된 문서들
        chat_history: 이전 대화 기록 (선택적)
    """
    try:
        # 1. 검색된 문서들을 컨텍스트로 변환
        context = "\n\n".join([doc["content"] for doc in retrieved_docs])
        
        # 2. 대화 기록이 있다면 컨텍스트에 추가
        if chat_history:
            conversation_context = "\n".join([
                f"{'사용자' if msg['role'] == 'user' else '어시스턴트'}: {msg['content']}"
                for msg in chat_history
            ])
            context = f"이전 대화 내용:\n{conversation_context}\n\n검색된 문서 내용:\n{context}"

        # 3. 프롬프트 구성
        prompt = f"""다음 문서와 이전 대화 내용을 참고하여 질문에 답변해주세요.

문서 내용:
{retrieved_docs}

이전 대화 내용:
{chat_history}

질문: {query}

지시사항:
1. 이전 대화 내용을 먼저 확인하고, 사용자의 질문 의도를 파악하세요.
2. 이전 대화에서 이미 언급된 내용이나 답변된 내용이 있다면, 그것을 참고하여 답변하세요.
3. 이전 대화 내용으로 답변할 수 없는 경우에만 문서 내용을 참고하세요.
4. 문서에 없는 내용은 추측하지 마세요.
5. 이전 대화에서 이미 언급된 내용은 반복하지 마세요.

답변:"""

        # 4. Gemini API 호출
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        logger.error(f"Error in create_answer_with_gemini: {str(e)}")
        raise
