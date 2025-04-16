from typing import Dict, List, Optional
from langchain.memory import ConversationBufferWindowMemory
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatMemoryManager:
    def __init__(self, max_history_size: int = 10):
        """채팅 메모리 관리자를 초기화합니다."""
        self.max_history_size = max_history_size
        self.conversations = {}  # {product_id}_{user_id}: [messages]
        self.last_accessed = {}  # {product_id}_{user_id}: timestamp
        logger.info(f"Initialized ChatMemoryManager with max_history_size: {max_history_size}")

    def _get_memory_key(self, product_id: str, user_id: str) -> str:
        """메모리 키를 생성합니다."""
        return f"{product_id}_{user_id}"

    def add_message(self, product_id: str, user_id: str, message: str, is_user: bool) -> None:
        """새로운 메시지를 대화 기록에 추가합니다."""
        try:
            memory_key = self._get_memory_key(product_id, user_id)
            
            if memory_key not in self.conversations:
                self.conversations[memory_key] = []
                logger.info(f"Created new conversation for key: {memory_key}")

            # 메시지 추가
            self.conversations[memory_key].append({
                'role': 'user' if is_user else 'assistant',
                'content': message
            })

            # 최대 크기 유지
            if len(self.conversations[memory_key]) > self.max_history_size:
                self.conversations[memory_key] = self.conversations[memory_key][-self.max_history_size:]
                logger.info(f"Trimmed conversation history for key: {memory_key}")

            # 접근 시간 업데이트
            self.last_accessed[memory_key] = time.time()
            logger.debug(f"Added message to conversation {memory_key}, current size: {len(self.conversations[memory_key])}")

        except Exception as e:
            logger.error(f"Error adding message: {str(e)}", exc_info=True)
            raise

    def get_chat_history(self, product_id: str, user_id: str) -> List[Dict[str, str]]:
        """특정 제품과 사용자의 대화 기록을 반환합니다."""
        try:
            memory_key = self._get_memory_key(product_id, user_id)
            
            if memory_key not in self.conversations:
                logger.info(f"No chat history found for key: {memory_key}")
                return []

            # 접근 시간 업데이트
            self.last_accessed[memory_key] = time.time()
            logger.debug(f"Retrieved chat history for key: {memory_key}, size: {len(self.conversations[memory_key])}")
            
            return self.conversations[memory_key]

        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}", exc_info=True)
            return []

    def clear_old_conversations(self, max_age_hours: int = 24) -> None:
        """오래된 대화 기록을 정리합니다."""
        try:
            current_time = time.time()
            keys_to_remove = []

            for memory_key, last_access in self.last_accessed.items():
                if current_time - last_access > max_age_hours * 3600:
                    keys_to_remove.append(memory_key)

            for key in keys_to_remove:
                del self.conversations[key]
                del self.last_accessed[key]
                logger.info(f"Removed old conversation: {key}")

        except Exception as e:
            logger.error(f"Error clearing old conversations: {str(e)}", exc_info=True)

    def print_all_conversations(self) -> None:
        """모든 대화 기록의 상태를 출력합니다."""
        try:
            logger.info("=== Current Memory State ===")
            for memory_key, messages in self.conversations.items():
                logger.info(f"Key: {memory_key}")
                logger.info(f"Messages count: {len(messages)}")
                logger.info(f"Last accessed: {datetime.fromtimestamp(self.last_accessed[memory_key])}")
                logger.info("---")
        except Exception as e:
            logger.error(f"Error printing conversations: {str(e)}", exc_info=True)

# 전역 인스턴스 생성
chat_memory_manager = ChatMemoryManager() 