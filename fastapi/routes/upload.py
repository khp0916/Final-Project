from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from services.storage import get_vector_store
from services.embedding import get_embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import PyPDF2
import io
import logging
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("")
async def upload_endpoint(
    file: UploadFile = File(...), 
    category_id: int = Form(...),
    name: str = Form(...),
    product_id: int = Form(...),
    chunk_size: int = Form(210),
    chunk_overlap: int = Form(50)
):
    """PDF 파일을 업로드하고 처리"""
    try:
        # 파일 내용 읽기
        file_content = await file.read()
        
        # PDF 텍스트 추출
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # 텍스트 분할
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_text(text)
        
        # 컬렉션 생성
        collection_name = f"product_{product_id}_embeddings"
        collection_uuid = str(uuid.uuid4())
        
        # 임베딩 생성 및 저장
        embeddings = get_embeddings()
        vector_store = get_vector_store(collection_name, embeddings)
        
        saved_chunks = 0
        for i, chunk in enumerate(chunks):
            try:
                # 메타데이터 생성
                metadata = {
                    "chunk_index": i,
                    "source": file.filename,
                    "category_id": category_id,
                    "product_id": product_id,
                    "product_name": name,
                    "created_at": datetime.now().isoformat()
                }
                
                # 벡터DB에 저장 (임베딩은 embedding_function이 처리)
                vector_store.add_texts(
                    texts=[chunk],
                    metadatas=[metadata]
                )
                saved_chunks += 1
                
            except Exception as e:
                logger.warn(f"임베딩 실패 (index: {i}): {chunk[:50]}...")
                logger.error(f"Error details: {str(e)}")
        
        return {
            "status": "success",
            "collection_name": collection_name,
            "collection_uuid": collection_uuid,
            "chunks_saved": saved_chunks
        }
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"파일 처리 중 오류 발생: {str(e)}")
