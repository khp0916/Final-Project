from typing import Dict, Any, List, Optional
import httpx
import logging
import os
from services.chat_memory import chat_memory_manager
from services.storage import search_documents_with_answer

logger = logging.getLogger(__name__)
SPRINGBOOT_API_URL = os.getenv("SPRINGBOOT_API_URL", "http://localhost:8080")

class ChatService:
    def __init__(self):
        self.memory_manager = chat_memory_manager
        logger.info("ChatService initialized")

    async def get_chat_history_from_spring(self, product_id: int, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Spring Boot API에서 채팅 기록을 가져옵니다."""
        if user_id is None:
            logger.warning("User ID is required for chat history")
            return []
        
        try:
            spring_url = f"{SPRINGBOOT_API_URL}/api/chat/history?productId={product_id}&userId={user_id}"
            logger.info(f"Requesting chat history from Spring Boot - URL: {spring_url}")
            
            async with httpx.AsyncClient() as client:
                logger.info("Sending request to Spring Boot...")
                response = await client.get(spring_url)
                logger.info(f"Response status code: {response.status_code}")
                
                if response.status_code == 400:
                    logger.warning("Bad request - User ID is required")
                    return []
                    
                response.raise_for_status()
                history = response.json()
                logger.info(f"Retrieved {len(history)} chat history records")
                
                # Spring Boot의 응답 형식을 FastAPI의 메모리 형식으로 변환
                formatted_history = []
                for item in history:
                    formatted_history.append({
                        "role": "user",
                        "content": item["queryText"]
                    })
                    formatted_history.append({
                        "role": "assistant",
                        "content": item["responseText"]
                    })
                
                logger.info(f"Formatted {len(formatted_history)} messages for memory")
                return formatted_history
        except Exception as e:
            logger.error(f"Error fetching chat history from Spring Boot: {str(e)}", exc_info=True)
            return []

    async def process_message(
        self,
        product_id: str,
        message: str,
        user_id: Optional[str] = None,
        collection_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """메시지를 처리하고 응답을 생성합니다."""
        try:
            logger.info(f"Processing message - Product: {product_id}, User: {user_id}, Message: {message}")
            
            # 메모리 키 생성
            memory_key = f"{product_id}_{user_id}" if user_id else f"{product_id}_anonymous"
            
            # 현재 메모리 상태 확인
            current_memory = self.memory_manager.get_chat_history(product_id, user_id)
            logger.info(f"Current memory state for {memory_key}: {len(current_memory)} messages")
            
            # Spring Boot에서 채팅 기록 가져오기 (사용자가 있고 메모리가 비어있는 경우에만)
            if user_id and not current_memory:
                spring_history = await self.get_chat_history_from_spring(product_id, user_id)
                if spring_history:
                    logger.info(f"Retrieved {len(spring_history)} messages from Spring Boot")
                    for msg in spring_history:
                        self.memory_manager.add_message(
                            product_id=product_id,
                            message=msg["content"],
                            is_user=msg["role"] == "user",
                            user_id=user_id
                        )
                    current_memory = self.memory_manager.get_chat_history(product_id, user_id)
            
            # 현재 메시지를 메모리에 추가
            self.memory_manager.add_message(
                product_id=product_id,
                message=message,
                is_user=True,
                user_id=user_id
            )
            
            # 컨텍스트 생성 (이전 대화 기록 포함)
            context = []
            if current_memory:
                context.append("이전 대화 내용:")
                for msg in current_memory:
                    role = "사용자" if msg["role"] == "user" else "AI"
                    context.append(f"{role}: {msg['content']}")
                context.append("")  # 빈 줄 추가
            
            # 문서 검색 및 답변 생성
            result = await search_documents_with_answer(
                query_text=message,
                collection_name=collection_name or f"product_{product_id}_embeddings",
                context="\n".join(context)
            )
            
            # 응답을 메모리에 추가
            self.memory_manager.add_message(
                product_id=product_id,
                message=result["answer"],
                is_user=False,
                user_id=user_id
            )
            
            # 메모리 상태 출력 (디버깅용)
            self.memory_manager.print_all_conversations()
            
            # 현재 메모리 상태 다시 가져오기
            current_memory = self.memory_manager.get_chat_history(product_id, user_id)
            
            return {
                "answer": result["answer"],
                "context": result["documents"],
                "memory": current_memory
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            raise

    async def get_chat_history(self, product_id: int) -> List[Dict[str, Any]]:
        """채팅 기록을 조회합니다."""
        try:
            logger.info(f"Getting chat history for product_id={product_id}")
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{SPRINGBOOT_API_URL}/api/chat/history",
                    params={"productId": product_id}
                )
                if response.status_code == 200:
                    history = response.json()
                    logger.info(f"Retrieved {len(history)} chat history records")
                    return history
                logger.warning(f"Failed to fetch chat history: status_code={response.status_code}")
                return []
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}", exc_info=True)
            raise

# 전역 인스턴스 생성
chat_service = ChatService() 