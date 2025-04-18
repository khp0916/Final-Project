from typing import List, Dict, Optional
import time
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage, HumanMessage, AIMessage
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatMemoryManager:
    def __init__(self, max_history_size: int = 10):
        """채팅 메모리 관리자를 초기화합니다."""
        self.max_history_size = max_history_size
        self.memories = {}  # {product_id}_{user_id}: ConversationBufferWindowMemory
        self.last_accessed = {}  # {product_id}_{user_id}: timestamp
        logger.info(f"Initialized ChatMemoryManager with max_history_size: {max_history_size}")

    def _get_memory_key(self, product_id: str, user_id: Optional[str] = None) -> str:
        """메모리 키를 생성합니다."""
        return f"{product_id}_{user_id}" if user_id else f"{product_id}_anonymous"

    def _get_or_create_memory(self, product_id: str, user_id: Optional[str] = None) -> ConversationBufferWindowMemory:
        """메모리 객체를 가져오거나 생성합니다."""
        memory_key = self._get_memory_key(product_id, user_id)
        
        if memory_key not in self.memories:
            self.memories[memory_key] = ConversationBufferWindowMemory(
                k=self.max_history_size,
                return_messages=True
            )
            self.last_accessed[memory_key] = time.time()
        
        return self.memories[memory_key]

    def add_message(self, product_id: str, message: str, is_user: bool, user_id: Optional[str] = None) -> None:
        """새로운 메시지를 메모리에 추가합니다."""
        try:
            memory_key = self._get_memory_key(product_id, user_id)
            memory = self._get_or_create_memory(product_id, user_id)
            
            if is_user:
                memory.chat_memory.add_user_message(message)
            else:
                memory.chat_memory.add_ai_message(message)
            
            self.last_accessed[memory_key] = time.time()
            logger.debug(f"Added message to conversation {memory_key}, current size: {len(memory.chat_memory.messages)}")

        except Exception as e:
            logger.error(f"Error adding message: {str(e)}", exc_info=True)
            raise

    def get_chat_history(self, product_id: str, user_id: Optional[str] = None) -> List[Dict[str, str]]:
        """특정 제품과 사용자의 대화 기록을 반환합니다."""
        try:
            memory = self._get_or_create_memory(product_id, user_id)
            messages = memory.chat_memory.messages
            
            # 메시지를 Dict 형식으로 변환
            history = []
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    history.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    history.append({"role": "assistant", "content": msg.content})
            
            # 접근 시간 업데이트
            memory_key = self._get_memory_key(product_id, user_id)
            self.last_accessed[memory_key] = time.time()
            logger.debug(f"Retrieved chat history for key: {memory_key}, size: {len(history)}")
            
            return history

        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}", exc_info=True)
            return []

    def clear_old_conversations(self, max_age_seconds: int = 3600) -> None:
        """오래된 대화 기록을 정리합니다."""
        try:
            current_time = time.time()
            keys_to_remove = []

            for key, last_access in self.last_accessed.items():
                if current_time - last_access > max_age_seconds:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                del self.memories[key]
                del self.last_accessed[key]
                logger.info(f"Removed old conversation: {key}")

        except Exception as e:
            logger.error(f"Error clearing old conversations: {str(e)}", exc_info=True)

    def print_all_conversations(self) -> None:
        """모든 대화 기록의 상태를 출력합니다."""
        try:
            logger.info("=== Current Memory State ===")
            for key, memory in self.memories.items():
                logger.info(f"Conversation: {key}")
                messages = memory.chat_memory.messages
                for msg in messages:
                    role = "User" if isinstance(msg, HumanMessage) else "Assistant"
                    logger.info(f"{role}: {msg.content}")
                logger.info(f"Last accessed: {datetime.fromtimestamp(self.last_accessed[key])}")
                logger.info("---")
        except Exception as e:
            logger.error(f"Error printing conversations: {str(e)}", exc_info=True)

# 전역 인스턴스 생성
chat_memory_manager = ChatMemoryManager() 