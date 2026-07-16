from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List
import os

from app.utils.db import get_db
from app.models.document import Document, User, DocumentChunk
from app.schemas.document import DocumentResponse, DocumentDetailResponse
from app.services.pdf_service import PDFValidator, PDFMetadataExtractor
from app.services.text_extraction_service import TextExtractor
from app.services.chunking_service import ChunkingService

router = APIRouter(prefix="/api/documents", tags=["documents"])

def get_default_user(db: Session) -> str:
    """Get or create default user"""
    default_user_id = "00000000-0000-0000-0000-000000000001"
    
    user = db.query(User).filter(User.id == default_user_id).first()
    
    if not user:
        user = User(id=default_user_id, email="test@documind.local")
        db.add(user)
        db.commit()
    
    return str(user.id)

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a PDF document"""
    
    try:
        file_content = await file.read()
        
        is_valid, error_message = PDFValidator.validate(
            file_content,
            file.filename or "unknown.pdf",
            file.content_type or "application/octet-stream"
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        metadata = PDFMetadataExtractor.extract_basic_metadata(file_content)
        
        user_id = get_default_user(db)
        
        document = Document(
            id=uuid4(),
            user_id=user_id,
            filename=file.filename or "unknown.pdf",
            file_content=file_content,
            file_size_bytes=len(file_content),
            mime_type=file.content_type or "application/pdf",
            pdf_metadata=metadata,
            status="uploaded"
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return {
            "id": document.id,
            "filename": document.filename,
            "file_size_bytes": document.file_size_bytes,
            "mime_type": document.mime_type,
            "status": document.status,
            "created_at": document.created_at
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload: {str(e)}"
        )

@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Get document metadata"""
    
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found"
            )
        
        return {
            "id": document.id,
            "filename": document.filename,
            "file_size_bytes": document.file_size_bytes,
            "mime_type": document.mime_type,
            "status": document.status,
            "pdf_metadata": document.pdf_metadata,
            "created_at": document.created_at,
            "updated_at": document.updated_at
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching document: {str(e)}"
        )

@router.get("", response_model=List[DocumentResponse])
async def list_documents(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List all documents"""
    
    try:
        documents = db.query(Document)\
            .offset(skip)\
            .limit(limit)\
            .order_by(Document.created_at.desc())\
            .all()
        
        return [
            {
                "id": doc.id,
                "filename": doc.filename,
                "file_size_bytes": doc.file_size_bytes,
                "mime_type": doc.mime_type,
                "status": doc.status,
                "created_at": doc.created_at
            }
            for doc in documents
        ]
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing documents: {str(e)}"
        )

@router.post("/{document_id}/process")
async def process_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Process PDF: extract text and create chunks"""
    
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found"
            )
        
        document.status = "processing"
        db.commit()
        
        import time
        start_time = time.time()
        
        # Extract text
        extraction_result = TextExtractor.extract_all(document.file_content)
        extracted_text = extraction_result["text"]
        
        if not extracted_text.strip():
            document.status = "processing_failed"
            document.pdf_metadata["error"] = "No text extracted"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No text extracted from PDF"
            )
        
        # Chunk text
        chunker = ChunkingService(max_tokens=800, overlap_tokens=100)
        chunks = chunker.chunk_text(extracted_text)
        
        if not chunks:
            document.status = "processing_failed"
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create chunks"
            )
        
        # Store chunks
        for chunk_data in chunks:
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=chunk_data["chunk_index"],
                content=chunk_data["content"],
                token_count=chunk_data["token_count"],
                page_number=chunk_data["page_number"]
            )
            db.add(chunk)
        
        processing_time = time.time() - start_time
        document.status = "processed"
        document.pdf_metadata["chunks_created"] = len(chunks)
        document.pdf_metadata["processing_time_seconds"] = processing_time
        
        db.commit()
        db.refresh(document)
        
        return {
            "document_id": document_id,
            "status": "success",
            "chunks_created": len(chunks),
            "processing_time_seconds": round(processing_time, 2),
            "total_tokens": sum(c["token_count"] for c in chunks)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing: {str(e)}"
        )

@router.get("/{document_id}/chunks")
async def get_document_chunks(
    document_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get chunks for a document"""
    
    try:
        chunks = db.query(DocumentChunk)\
            .filter(DocumentChunk.document_id == document_id)\
            .order_by(DocumentChunk.chunk_index)\
            .offset(skip)\
            .limit(limit)\
            .all()
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No chunks found"
            )
        
        return [
            {
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "content": chunk.content[:200] + "..." if len(chunk.content) > 200 else chunk.content,
                "token_count": chunk.token_count,
                "page_number": chunk.page_number
            }
            for chunk in chunks
        ]
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching chunks: {str(e)}"
        )

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """Delete a document"""
    
    try:
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found"
            )
        
        db.delete(document)
        db.commit()
        
        return {
            "message": "Document deleted",
            "document_id": document_id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting: {str(e)}"
        )