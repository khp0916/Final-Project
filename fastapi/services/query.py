import re
from typing import Dict, Any
from services.storage import search_documents
from services.llm import create_answer_with_gemini

async def search_documents_with_answer(query_text: str, collection_name: str, context: str = "", top_k: int = 3) -> Dict[str, Any]:
    """벡터 저장소에서 유사 문서를 검색하고 답변을 생성"""
    try:
        # 벡터 저장소에서 유사 문서 검색
        search_results = await search_documents(query_text, collection_name, top_k)
        
        # 문서 내용 정규화
        normalized_docs = []
        for doc in search_results["documents"]:
            content = re.sub(r'\s+', ' ', doc["content"]).strip()
            normalized_docs.append({
                "content": content,
                "metadata": doc["metadata"],
                "score": doc["score"]
            })
        
        # 컨텍스트를 대화 기록 형식으로 변환
        chat_history = []
        if context:
            # 컨텍스트를 줄별로 분리
            lines = context.strip().split('\n')
            current_role = None
            current_content = []
            
            for line in lines:
                if line.startswith('사용자:') or line.startswith('AI:'):
                    # 이전 메시지가 있었다면 저장
                    if current_role and current_content:
                        chat_history.append({
                            'role': 'user' if current_role == '사용자' else 'assistant',
                            'content': '\n'.join(current_content).strip()
                        })
                    
                    # 새 메시지 시작
                    current_role = '사용자' if line.startswith('사용자:') else 'assistant'
                    current_content = [line.split(':', 1)[1].strip()]
                else:
                    current_content.append(line)
            
            # 마지막 메시지 저장
            if current_role and current_content:
                chat_history.append({
                    'role': 'user' if current_role == '사용자' else 'assistant',
                    'content': '\n'.join(current_content).strip()
                })
        
        # Gemini로 답변 생성
        answer = await create_answer_with_gemini(query_text, normalized_docs, chat_history)
        
        return {
            "query": query_text,
            "documents": normalized_docs,
            "answer": answer
        }
    except Exception as e:
        raise Exception(f"문서 검색 및 답변 생성 중 오류 발생: {str(e)}")
