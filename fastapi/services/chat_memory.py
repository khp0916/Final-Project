from typing import Dict, List, Optional
from langchain.memory import ConversationBufferWindowMemory
import logging

logger = logging.getLogger(__name__)

class ChatMemoryManager:
    def __init__(self, k: int = 10):
        """채팅 메모리 관리자를 초기화합니다.
        
        Args:
            k (int): 메모리에 저장할 대화의 최대 개수
        """
        self.memories: Dict[str, ConversationBufferWindowMemory] = {}
        self.k = k
        logger.info(f"Initialized ChatMemoryManager with window size {k}")

    def _get_memory_key(self, product_id: str, user_id: str) -> str:
        """메모리 키를 생성합니다."""
        return f"{product_id}_{user_id}"

    def _get_or_create_memory(self, product_id: str, user_id: str) -> ConversationBufferWindowMemory:
        """메모리를 가져오거나 생성합니다."""
        memory_key = self._get_memory_key(product_id, user_id)
        if memory_key not in self.memories:
            logger.info(f"Creating new memory for product {product_id} and user {user_id}")
            self.memories[memory_key] = ConversationBufferWindowMemory(
                k=self.k,
                return_messages=True
            )
        return self.memories[memory_key]

    def add_message(self, product_id: str, user_id: str, message: str, is_user: bool) -> None:
        """메시지를 메모리에 추가합니다."""
        try:
            memory = self._get_or_create_memory(product_id, user_id)
            role = "human" if is_user else "ai"
            memory.chat_memory.add_message(
                {"role": role, "content": message}
            )
            logger.info(f"Added message to memory - Product: {product_id}, User: {user_id}, Role: {role}")
        except Exception as e:
            logger.error(f"Error adding message to memory: {str(e)}", exc_info=True)
            raise

    def get_chat_history(self, product_id: str, user_id: str) -> List[Dict[str, str]]:
        """채팅 기록을 가져옵니다."""
        try:
            memory = self._get_or_create_memory(product_id, user_id)
            messages = memory.chat_memory.messages
            history = []
            for msg in messages:
                history.append({
                    "role": msg.type,
                    "content": msg.content
                })
            logger.info(f"Retrieved {len(history)} messages from memory for product {product_id} and user {user_id}")
            return history
        except Exception as e:
            logger.error(f"Error getting chat history: {str(e)}", exc_info=True)
            return []

    def clear_memory(self, product_id: str, user_id: str) -> None:
        """메모리를 초기화합니다."""
        try:
            memory_key = self._get_memory_key(product_id, user_id)
            if memory_key in self.memories:
                del self.memories[memory_key]
                logger.info(f"Cleared memory for product {product_id} and user {user_id}")
        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}", exc_info=True)
            raise

    def print_all_conversations(self) -> None:
        """모든 대화 기록을 출력합니다."""
        try:
            logger.info("=== Current Memory State ===")
            for memory_key, memory in self.memories.items():
                product_id, user_id = memory_key.split("_")
                logger.info(f"\nProduct: {product_id}, User: {user_id}")
                messages = memory.chat_memory.messages
                for msg in messages:
                    logger.info(f"{msg.type}: {msg.content}")
            logger.info("=== End of Memory State ===")
        except Exception as e:
            logger.error(f"Error printing conversations: {str(e)}", exc_info=True)

# 전역 인스턴스 생성
chat_memory_manager = ChatMemoryManager() 