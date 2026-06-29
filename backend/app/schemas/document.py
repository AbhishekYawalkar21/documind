from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime
from uuid import UUID

class DocumentResponse(BaseModel):
    id: UUID
    filename: str
    file_size_bytes: int
    mime_type: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentDetailResponse(BaseModel):
    id: UUID
    filename: str
    file_size_bytes: int
    mime_type: str
    status: str
    pdf_metadata: Optional[Dict] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class AnalysisResultResponse(BaseModel):
    id: UUID
    document_id: UUID
    summary: Optional[str] = None
    topics: List[str] = []
    entities: Dict = {}
    compliance_flags: List[Dict] = []
    knowledge_graph: List[Dict] = []
    analysis_status: str
    processing_time_seconds: Optional[float] = None
    
    class Config:
        from_attributes = True

class HealthResponse(BaseModel):
    status: str
    service: str
    database: str = "unknown"