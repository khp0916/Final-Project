import os
import json
import httpx
from typing import List, Dict, Any
from dotenv import load_dotenv
from services.embedding import get_embeddings, get_llm
from langchain_postgres import PGVector
# from langchain_community.document_loaders import PyMuPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# import tempfile
from services.llm import create_answer_with_gemini
import re

load_dotenv()

# ✅ Upstage 임베딩 모델 한 번만 생성 (매번 생성하지 않음)
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
        print("Successfully created PGVector instance")
        return vector_store
    except Exception as e:
        print(f"Error creating PGVector instance: {str(e)}")
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

async def search_documents(query_text: str, collection_name: str, top_k: int = 3, embeddings=None) -> Dict[str, Any]:
    """벡터 저장소에서 유사 문서를 검색하고 답변을 생성합니다."""
    try:
        print(f"Searching documents for query: {query_text}")
        print(f"Using collection: {collection_name}")
        
        vector_store = get_vector_store(collection_name, embeddings)
        docs_and_scores = vector_store.similarity_search_with_score(query_text, k=top_k)
        
        print(f"Found {len(docs_and_scores)} documents")
        
        results = []
        for doc, score in docs_and_scores:
            normalized_content = re.sub(r'\s+', ' ', doc.page_content).strip()
            results.append({
                "content": normalized_content,
                "metadata": doc.metadata,
                "score": score
            })
            print(f"Document score: {score}")

        answer = await create_answer_with_gemini(query_text, results)
        
        return {
            "query": query_text,
            "answer": answer,
            "documents": results
        }
        
    except Exception as e:
        print(f"Error in search_documents: {str(e)}")
        raise Exception(f"문서 검색 중 오류 발생: {str(e)}")
