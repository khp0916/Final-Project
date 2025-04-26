import os
import json
import httpx
import re
from typing import List, Dict, Any
from dotenv import load_dotenv
from services.embedding import get_embeddings
from langchain_postgres import PGVector
# from langchain_community.document_loaders import PyMuPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# import tempfile
from services.llm import create_answer_with_gemini, create_product_explanation
import logging

logger = logging.getLogger(__name__)
load_dotenv()

# ✅ Upstage 임베딩 모델 한 번만 생성
embeddings = get_embeddings()

def get_vector_store(collection_name, embeddings=None):
    """벡터 저장소 인스턴스를 반환합니다."""
    if not embeddings:
        embeddings = get_embeddings()
    
    # 환경 변수에서 데이터베이스 연결 정보 가져오기
    POSTGRES_USER = os.getenv("POSTGRES_USER")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "gigigenie")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT")
    
    # 연결 문자열 구성
    connection = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    
    try:
        vector_store = PGVector(
            embeddings=embeddings,
            collection_name=collection_name,
            connection=connection
        )
        logger.info("Successfully created PGVector instance")
        return vector_store
    except Exception as e:
        logger.error(f"Error creating PGVector instance: {str(e)}")
        raise

# async def process_pdf(file_content: bytes, file_name: str, collection_name: str = "langchain", chunk_size: int = 210, chunk_overlap: int = 50) -> Dict[str, Any]:
#     """PDF 파일을 Spring Boot API를 통해 처리"""
#     try:
#         # ✅ 벡터 임베딩 생성
#         vector = embeddings.embed_query(file_name)  

#         import json

#         async with httpx.AsyncClient() as client:
#             files = {'file': (file_name, file_content, 'application/pdf')}
#             data = {
#                 'collection_name': collection_name,
#                 'chunk_size': str(chunk_size),
#                 'chunk_overlap': str(chunk_overlap),
#                 'embedding': [vector]
#             }
#             response = await client.post(f"{SPRINGBOOT_API_URL}/api/upload", files=files, data=data)

#             if response.status_code != 200:
#                 error_detail = response.text if response.text else "No error details available"
#                 raise Exception(f"SpringBoot API error ({response.status_code}): {error_detail}")
                
#             return response.json()
#     except httpx.RequestError as e:
#         raise Exception(f"SpringBoot API connection error: {str(e)}")
#     except Exception as e:
#         raise Exception(f"SpringBoot API error: {str(e)}")

# async def list_collections() -> List[str]:
#     """Spring Boot API를 통해 컬렉션 목록을 조회"""
#     try:
#         async with httpx.AsyncClient() as client:
#             response = await client.get(f"{SPRINGBOOT_API_URL}/api/collections")
            
#             if response.status_code != 200:
#                 error_detail = response.text if response.text else "No error details available"
#                 raise Exception(f"SpringBoot API error ({response.status_code}): {error_detail}")
                
#             return response.json()
#     except httpx.RequestError as e:
#         raise Exception(f"SpringBoot API connection error: {str(e)}")
#     except Exception as e:
#         raise Exception(f"SpringBoot API error: {str(e)}")

async def search_documents_with_answer(
    query_text: str, 
    collection_name: str, 
    context: str = "", 
    top_k: int = 3
) -> Dict[str, Any]:
    """벡터 저장소에서 유사 문서를 검색하고 답변을 생성합니다."""
    try:
        logger.info(f"Searching documents for query: {query_text}")
        logger.info(f"Using collection: {collection_name}")
        
        # 1. 벡터 저장소에서 유사 문서 검색
        vector_store = get_vector_store(collection_name)
        docs_and_scores = vector_store.similarity_search_with_score(query_text, k=top_k)
        
        logger.info(f"Found {len(docs_and_scores)} documents")
        
        # 2. 문서 내용 정규화
        results = []
        for doc, score in docs_and_scores:
            normalized_content = re.sub(r'\s+', ' ', doc.page_content).strip()
            results.append({
                "content": normalized_content,
                "metadata": doc.metadata,
                "score": score
            })
            logger.debug(f"Document score: {score}")

        # 3. 컨텍스트를 대화 기록 형식으로 변환
        chat_history = []
        if context:
            lines = context.strip().split('\n')
            current_role = None
            current_content = []
            
            for line in lines:
                if line == "이전 대화 내용:":
                    continue
                elif line.startswith('사용자:') or line.startswith('AI:'):
                    if current_role and current_content:
                        chat_history.append({
                            'role': 'user' if current_role == '사용자' else 'assistant',
                            'content': '\n'.join(current_content).strip()
                        })
                    current_role = '사용자' if line.startswith('사용자:') else 'assistant'
                    current_content = [line.split(':', 1)[1].strip()]
                elif line.strip():  # 빈 줄이 아닌 경우에만 내용에 추가
                    current_content.append(line)
            
            if current_role and current_content:
                chat_history.append({
                    'role': 'user' if current_role == '사용자' else 'assistant',
                    'content': '\n'.join(current_content).strip()
                })
            
            logger.info(f"Converted context to chat history: {len(chat_history)} messages")

        # 4. Gemini로 답변 생성
        answer = await create_answer_with_gemini(query_text, results, chat_history)
        logger.info("Generated answer from Gemini")
        
        return {
            "query": query_text,
            "answer": answer,
            "documents": results
        }
        
    except Exception as e:
        logger.error(f"Error in search_documents_with_answer: {str(e)}", exc_info=True)
        raise Exception(f"문서 검색 및 답변 생성 중 오류 발생: {str(e)}")

async def search_products_by_query(
    query: str,
    collection_name: str,
    top_k: int = 3
) -> Dict[str, Any]:
    """사용자의 자연어 입력을 기반으로 유사한 제품을 검색하고 설명을 생성합니다."""
    try:
        logger.info(f"Searching products with query: {query}")
        logger.info(f"Using collection: {collection_name}")
        
        # 벡터 저장소에서 유사 문서 검색
        vector_store = get_vector_store(collection_name)
        docs_and_scores = vector_store.similarity_search_with_score(query, k=top_k)
        
        logger.info(f"Found {len(docs_and_scores)} products")
        
        # 검색 결과에서 제품 정보 추출
        products = []
        for doc, score in docs_and_scores:
            if 'product_id' in doc.metadata:
                products.append({
                    "product_id": doc.metadata['product_id'],
                    "content": doc.page_content,
                    "score": score
                })
                logger.debug(f"Product ID: {doc.metadata['product_id']}, Score: {score}")

        # 제품 검색 전용 LLM 함수로 설명 생성
        explanation = await create_product_explanation(query, products)
        
        return {
            "query": query,
            "answer": explanation,
            "products": products
        }
        
    except Exception as e:
        logger.error(f"Error in search_products_by_query: {str(e)}", exc_info=True)
        raise Exception(f"제품 검색 중 오류 발생: {str(e)}")

# 함수를 모듈 레벨에서 export
__all__ = ['search_documents_with_answer', 'search_products_by_query']
