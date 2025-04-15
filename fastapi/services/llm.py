# services/llm.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import List, Dict

load_dotenv()

# API 키 확인
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY 환경 변수가 설정되지 않았습니다.")

genai.configure(api_key=api_key)

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
        prompt = f"""당신은 도움이 되는 AI 어시스턴트입니다. 
아래 제공된 문서 내용을 바탕으로 사용자의 질문에 정확하게 답변해주세요.

{context}

사용자의 질문: {query}

위 문서 내용을 바탕으로 사용자의 질문에 대해 정확도가 높고 사용자가 쉽게 이해할 수 있게 설명해주세요.
문서 내용에 없는 정보는 추측하지 마세요."""

        # 4. Gemini API 호출
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Error in create_answer_with_gemini: {str(e)}")
        raise
