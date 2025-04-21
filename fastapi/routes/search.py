# routes/search.py
from fastapi import APIRouter, HTTPException
from services import search_documents_with_answer, search_products_by_query
from models.schema import SearchQuery, SearchResponse
from pydantic import BaseModel
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SearchQuery(BaseModel):
    query: str
    collection_name: str
    top_k: Optional[int] = 3

class ProductFeatureSearch(BaseModel):
    query: str
    collection_name: str
    top_k: Optional[int] = 3

@router.post("/query")
async def search_query(query: SearchQuery):
    """문서를 검색하고 답변을 생성합니다."""
    try:
        logger.info(f"Received search query: {query.query}")
        logger.info(f"Collection: {query.collection_name}")
        
        result = await search_documents_with_answer(
            query_text=query.query,
            collection_name=query.collection_name,
            top_k=query.top_k
        )
        
        logger.info("Successfully generated search results")
        return result
        
    except Exception as e:
        logger.error(f"Error processing search query: {str(e)}", exc_info=True)
        raise

@router.post("/product/ai-search")
async def search_by_features(search: ProductFeatureSearch):
    """사용자의 자연어 입력을 기반으로 유사한 제품을 검색합니다."""
    try:
        logger.info(f"Received search request: {search.query}")
        logger.info(f"Collection: {search.collection_name}")
        
        result = await search_products_by_query(
            query=search.query,
            collection_name=search.collection_name,
            top_k=search.top_k
        )
        
        logger.info("Successfully generated search results")
        return {
            "query": result["query"],
            "answer": result["answer"],
            "products": result["products"]
        }
        
    except Exception as e:
        logger.error(f"Error processing feature search: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

# @router.post("/upload")
# async def upload_endpoint(file: UploadFile = File(...), collection_name: str = Form("langchain")):
#     """PDF 파일을 업로드하고 처리"""
#     try:
#         # 파일 내용 읽기
#         file_content = await file.read()
        
#         # PDF 처리
#         result = await process_pdf(
#             file_content=file_content,
#             file_name=file.filename,
#             collection_name=collection_name
#         )
        
#         return result
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"파일 처리 중 오류 발생: {str(e)}")

# @router.get("/collections")
# async def list_collections_endpoint():
#     """컬렉션 목록 조회"""
#     try:
#         collections = await list_collections()
#         return collections
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"컬렉션 목록 조회 중 오류 발생: {str(e)}")
