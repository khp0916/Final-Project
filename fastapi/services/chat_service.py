from typing import Dict, Any, List, Optional
import httpx
import logging
import os
from services.chat_memory import chat_memory_manager
from services.llm import create_answer_with_gemini
from services.storage import search_documents

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

    async def process_message(self, product_id: str, message: str, user_id: str = None) -> str:
        """채팅 메시지를 처리하고 응답을 생성합니다."""
        try:
            logger.info("=== Processing Chat Message ===")
            logger.info(f"Product ID: {product_id}, User ID: {user_id}, Message: {message}")

            # Spring Boot에서 채팅 기록 가져오기
            chat_history = []
            if user_id:
                logger.info("Fetching chat history from Spring Boot...")
                chat_history = await self.get_chat_history_from_spring(int(product_id), int(user_id))
                logger.info(f"Retrieved {len(chat_history)} messages from Spring Boot")

            # 메모리에 이전 대화 기록 추가
            for chat in chat_history:
                logger.info(f"Adding message to memory - Role: {chat['role']}, Content: {chat['content']}")
                self.memory_manager.add_message(
                    product_id=product_id,
                    user_id=user_id or "guest",
                    message=chat['content'],
                    is_user=(chat['role'] == 'user')
                )

            # 현재 메시지를 메모리에 추가
            logger.info("Adding current message to memory")
            self.memory_manager.add_message(
                product_id=product_id,
                user_id=user_id or "guest",
                message=message,
                is_user=True
            )

            # 컨텍스트와 프롬프트 생성
            context = self._build_context(chat_history)
            prompt = self._build_prompt(message, context)

            # Gemini API로 응답 생성
            logger.info("Generating response with Gemini API...")
            response = await create_answer_with_gemini(prompt)
            logger.info(f"Generated response: {response}")

            # AI 응답을 메모리에 추가
            logger.info("Adding AI response to memory")
            self.memory_manager.add_message(
                product_id=product_id,
                user_id=user_id or "guest",
                message=response,
                is_user=False
            )

            # 디버깅을 위해 현재 메모리 상태 출력
            logger.info("Current memory state:")
            self.memory_manager.print_all_conversations()

            return response

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            raise

    async def get_chat_history(self, product_id: int) -> List[Dict[str, Any]]:
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

    def _build_prompt(self, message: str, context: str) -> str:
        """프롬프트를 생성합니다."""
        prompt = f"""당신은 도움이 되는 AI 어시스턴트입니다. 이전 대화 내용을 바탕으로 현재 질문에 상세하고 정확한 응답을 제공해주세요.

{context}

사용자: {message}

응답:"""
        return prompt

    def _build_context(self, chat_history: List[Dict[str, Any]]) -> str:
        """사용자의 채팅 기록을 컨텍스트로 변환합니다."""
        context_lines = []
        for chat in chat_history:
            role = "사용자" if chat['role'] == 'user' else "AI"
            context_lines.append(f"{role}: {chat['content']}")
            
        return "\n".join(context_lines)

    # Helper methods for adding messages to memory
    def add_user_message(self, product_id: int, message: str, user_id: int) -> None:
        """사용자 메시지를 메모리에 추가합니다."""
        self.memory_manager.add_message(str(product_id), str(user_id), message, is_user=True)
        
    def add_ai_message(self, product_id: int, message: str, user_id: int) -> None:
        """AI 응답을 메모리에 추가합니다."""
        self.memory_manager.add_message(str(product_id), str(user_id), message, is_user=False)

# 전역 인스턴스 생성
chat_service = ChatService() 