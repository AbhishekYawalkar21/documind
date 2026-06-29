from sqlalchemy import Column, String, Integer, DateTime, LargeBinary, Text, Float
from sqlalchemy.dialects.postgresql import JSONB, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from app.utils.db import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    file_content = Column(LargeBinary, nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    mime_type = Column(String(100), default="application/pdf")
    pdf_metadata = Column(JSONB, default={})
    status = Column(String(50), default="uploaded")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class DocumentChunk(Base):
    __tablename__ = "document_chunks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    document_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    start_position = Column(Integer)
    end_position = Column(Integer)
    page_number = Column(Integer)
    embedding = Column(String)
    token_count = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    summary = Column(Text)
    topics = Column(ARRAY(String), default=[])
    entities = Column(JSONB, default={})
    compliance_flags = Column(JSONB, default={})
    knowledge_graph = Column(JSONB, default={})
    raw_analysis = Column(JSONB)
    analysis_status = Column(String(50), default="pending")
    analysis_started_at = Column(DateTime)
    analysis_completed_at = Column(DateTime)
    processing_time_seconds = Column(Float)

class QAHistory(Base):
    __tablename__ = "qa_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    user_query = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    relevant_chunks = Column(ARRAY(Integer), default=[])
    confidence_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)