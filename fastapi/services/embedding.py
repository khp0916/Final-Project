import os
from langchain_openai import OpenAIEmbeddings
from langchain_upstage import ChatUpstage
from dotenv import load_dotenv

load_dotenv()
upstage_api_key = os.getenv('UPSTAGE_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
gemini_api_key = os.getenv('GEMINI_API_KEY')

def get_embeddings():
    """임베딩 모델을 초기화"""
    return OpenAIEmbeddings(
        model="text-embedding-3-small",
        openai_api_key=openai_api_key
    )

def get_llm():
    """LLM 모델을 초기화"""
    return ChatUpstage(
        model="solar-1-mini-chat",
        api_key=upstage_api_key
    )

