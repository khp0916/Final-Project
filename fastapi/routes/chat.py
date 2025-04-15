from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from services.chat_service import chat_service
import httpx
import logging
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatMessage(BaseModel):
    query: str
    collection_name: str
    top_k: int = 3
    user_id: Optional[int] = None

class ChatHistoryResponse(BaseModel):
    query_id: int
    product_id: int
    member_id: int
    query_text: str
    response_text: str
    query_time: int
    formatted_query_time: str

@router.post("/ask")
async def send_message(message: ChatMessage):
    """채팅 메시지를 처리하고 응답을 반환합니다."""
    try:
        logger.info(f"Received message - Query: {message.query}, Collection: {message.collection_name}, User ID: {message.user_id}")
        response = await chat_service.process_message(
            product_id=message.collection_name.replace("product_", "").replace("_embeddings", ""),
            message=message.query,
            user_id=str(message.user_id) if message.user_id else None
        )
        logger.info(f"Generated response: {response}")
        return {"answer": response}
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_chat_history(product_id: int, user_id: Optional[int] = None):
    """채팅 기록을 조회합니다."""
    try:
        logger.info(f"Fetching chat history - Product ID: {product_id}, User ID: {user_id}")
        history = await chat_service.get_chat_history(product_id)
        logger.info(f"Retrieved {len(history)} chat history records")
        return history
    except Exception as e:
        logger.error(f"Error fetching chat history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def get_chat_history_from_spring(product_id: int, user_id: Optional[int] = None):
    try:
        spring_url = f"{SPRINGBOOT_API_URL}/api/chat/history?productId={product_id}"
        if user_id:
            spring_url += f"&userId={user_id}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(spring_url)
            response.raise_for_status()
            history = response.json()
            
            # 데이터 형식 변환
            formatted_history = []
            for item in history:
                formatted_history.append({
                    "message": item["queryText"],
                    "answer": item["responseText"]
                })
            return formatted_history
    except Exception as e:
        print(f"Error fetching history: {str(e)}")
        return [] 