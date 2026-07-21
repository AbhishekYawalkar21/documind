from app.services.langgraph_agent import DocumentAnalysisAgent
from app.services.llm_service import LLMService
from app.services.qa_service import QAService
import uuid
import time
from threading import Thread
from sqlalchemy import update
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from typing import List
import os

from app.utils.db import get_db
from app.models.document import Document, User, DocumentChunk, AnalysisResult, QAHistory
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
                detail="Document not found"
            )
        
        return {
            "id": str(document.id),
            "filename": document.filename,
            "file_size_bytes": document.file_size_bytes,
            "mime_type": document.mime_type,
            "status": document.status,
            "pdf_metadata": document.pdf_metadata or {},
            "created_at": document.created_at.isoformat() if hasattr(document.created_at, "isoformat") else document.created_at,
            "updated_at": document.updated_at.isoformat() if hasattr(document.updated_at, "isoformat") else document.updated_at
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
        documents = (
            db.query(Document)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        
        return [
            {
                "id": str(doc.id),
                "filename": doc.filename,
                "file_size_bytes": doc.file_size_bytes,
                "mime_type": doc.mime_type,
                "status": doc.status,
                "created_at": doc.created_at.isoformat() if hasattr(doc.created_at, "isoformat") else doc.created_at
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

@router.post("/{document_id}/analyze")
async def analyze_document(
    document_id: str,
    db: Session = Depends(get_db)
):
    """
    Trigger document analysis using Ollama local LLM
    
    This endpoint:
    1. Fetches document and its chunks
    2. Runs multi-step analysis with local Ollama
    3. Stores results in database
    4. Returns analysis results
    
    - **document_id**: UUID of the document to analyze
    """
    
    try:
        # Fetch document
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found"
            )
        
        # Check if document has been processed
        chunks = db.query(DocumentChunk)\
            .filter(DocumentChunk.document_id == document_id)\
            .order_by(DocumentChunk.chunk_index)\
            .all()
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document not processed yet. Call /process endpoint first."
            )
        
        # Extract chunk content
        chunk_texts = [chunk.content for chunk in chunks]
        
        # Check if analysis already exists
        existing_analysis = db.query(AnalysisResult)\
            .filter(AnalysisResult.document_id == document_id)\
            .first()
        
        if existing_analysis and existing_analysis.analysis_status == "completed":
            return {
                "analysis_id": str(existing_analysis.id),
                "status": "analysis_exists",
                "message": "Document already analyzed",
                "completed_at": existing_analysis.analysis_completed_at
            }
        
        # Create analysis record
        analysis_id = str(uuid4())
        analysis = AnalysisResult(
            id=analysis_id,
            document_id=document_id,
            analysis_status="pending"
        )
        db.add(analysis)
        db.commit()
        
        # Run analysis in background
        def run_analysis():
            try:
                print(f"\n[BACKGROUND] Starting analysis for {document_id}")
                
                agent = DocumentAnalysisAgent()
                
                start_time = time.time()
                state = agent.execute(
                    document_id=str(document_id),
                    chunks=chunk_texts
                )
                processing_time = time.time() - start_time
                
                print(f"[BACKGROUND] Analysis complete in {processing_time:.2f}s")
                
                # Update database
                db.execute(
                    update(AnalysisResult).where(
                        AnalysisResult.id == analysis_id
                    ).values(
                        summary=state.summary,
                        topics=state.topics,
                        entities=state.entities,
                        compliance_flags=state.compliance_flags,
                        knowledge_graph=state.knowledge_graph,
                        raw_analysis=state.to_dict(),
                        analysis_status="completed",
                        analysis_completed_at=state.completed_at,
                        processing_time_seconds=processing_time
                    )
                )
                db.commit()
                
                print(f"[BACKGROUND] Results saved")
                
            except Exception as e:
                print(f"[BACKGROUND] Error: {str(e)}")
                db.execute(
                    update(AnalysisResult).where(
                        AnalysisResult.id == analysis_id
                    ).values(
                        analysis_status="failed",
                        raw_analysis={"error": str(e)}
                    )
                )
                db.commit()
        
        # Start background thread
        thread = Thread(target=run_analysis, daemon=True)
        thread.start()
        
        return {
            "analysis_id": analysis_id,
            "status": "analysis_started",
            "message": "Analysis started. Check status using analysis_id.",
            "document_id": str(document_id),
            "note": "⏳ First analysis takes longer as model loads"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting analysis: {str(e)}"
        )

@router.get("/{document_id}/analysis/{analysis_id}")
async def get_analysis_results(
    document_id: str,
    analysis_id: str,
    db: Session = Depends(get_db)
):
    """Get analysis results for a document"""
    
    try:
        analysis = db.query(AnalysisResult)\
            .filter(AnalysisResult.id == analysis_id)\
            .filter(AnalysisResult.document_id == document_id)\
            .first()
        
        if not analysis:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis not found"
            )
        
        if analysis.analysis_status == "pending":
            return {
                "analysis_id": analysis_id,
                "status": "pending",
                "message": "Analysis in progress...",
                "document_id": str(document_id)
            }
        
        if analysis.analysis_status == "failed":
            return {
                "analysis_id": analysis_id,
                "status": "failed",
                "error": analysis.raw_analysis.get("error", "Unknown error"),
                "document_id": str(document_id)
            }
        
        return {
            "analysis_id": analysis_id,
            "status": "completed",
            "document_id": str(document_id),
            "analysis": {
                "summary": analysis.summary,
                "topics": analysis.topics,
                "entities": analysis.entities,
                "compliance_flags": analysis.compliance_flags,
                "knowledge_graph": analysis.knowledge_graph
            },
            "processing_time_seconds": analysis.processing_time_seconds,
            "completed_at": analysis.analysis_completed_at
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching analysis: {str(e)}"
        )

@router.post("/{document_id}/question")
async def ask_question(
    document_id: str,
    question_data: dict,
    db: Session = Depends(get_db)
):
    """Ask a question about a document"""
    
    try:
        question = question_data.get("question", "").strip()
        
        if not question:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )
        
        # Fetch document
        document = db.query(Document).filter(Document.id == document_id).first()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document not found"
            )
        
        # Fetch chunks
        chunks = db.query(DocumentChunk)\
            .filter(DocumentChunk.document_id == document_id)\
            .order_by(DocumentChunk.chunk_index)\
            .all()
        
        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Document has no chunks. Process document first."
            )
        
        # Fetch latest analysis for summary
        analysis = db.query(AnalysisResult)\
            .filter(AnalysisResult.document_id == document_id)\
            .filter(AnalysisResult.analysis_status == "completed")\
            .order_by(AnalysisResult.analysis_completed_at.desc())\
            .first()
        
        # Prepare chunks for QA
        chunk_dicts = [
            {"id": idx, "content": chunk.content}
            for idx, chunk in enumerate(chunks)
        ]
        
        # Initialize QA service
        llm = LLMService()
        qa_service = QAService(llm)
        
        # Find relevant chunks
        relevant_chunks_with_scores = qa_service.find_relevant_chunks(
            question, chunk_dicts, top_k=3
        )
        
        relevant_chunk_ids = [item[0] for item in relevant_chunks_with_scores]
        relevant_chunk_contents = [item[1] for item in relevant_chunks_with_scores]
        
        # Generate answer
        answer, confidence = qa_service.answer_question(
            question,
            relevant_chunk_contents,
            document_summary=analysis.summary if analysis else None
        )
        
        # Store Q&A in database
        from app.models.document import QAHistory
        qa_record = QAHistory(
            id=uuid4(),
            document_id=document_id,
            user_query=question,
            ai_response=answer,
            relevant_chunks=relevant_chunk_ids,
            confidence_score=confidence
        )
        db.add(qa_record)
        db.commit()
        db.refresh(qa_record)
        
        return {
            "qa_id": str(qa_record.id),
            "question": question,
            "answer": answer,
            "confidence_score": round(confidence, 2),
            "relevant_chunks": relevant_chunk_ids,
            "document_id": str(document_id)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )

@router.get("/{document_id}/qa-history")
async def get_qa_history(
    document_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get Q&A history for a document"""
    
    try:
        from app.models.document import QAHistory
        
        qa_records = db.query(QAHistory)\
            .filter(QAHistory.document_id == document_id)\
            .offset(skip)\
            .limit(limit)\
            .order_by(QAHistory.created_at.desc())\
            .all()
        
        return {
            "document_id": str(document_id),
            "qa_count": len(qa_records),
            "qa_history": [
                {
                    "qa_id": str(qa.id),
                    "question": qa.user_query,
                    "answer": qa.ai_response[:200] + "..." if len(qa.ai_response) > 200 else qa.ai_response,
                    "confidence": round(qa.confidence_score or 0, 2),
                    "created_at": qa.created_at
                }
                for qa in qa_records
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching Q&A history: {str(e)}"
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