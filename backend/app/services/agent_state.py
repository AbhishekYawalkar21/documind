from typing import TypedDict, List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class DocumentAnalysisState:
    """State passed through LangGraph nodes"""
    
    # Input
    document_id: str
    chunks: List[str]
    
    # Processing
    analysis_step: str = "initialized"
    
    # Results
    summary: str = ""
    topics: List[str] = field(default_factory=list)
    entities: Dict = field(default_factory=dict)
    compliance_flags: List[Dict] = field(default_factory=list)
    knowledge_graph: List[Dict] = field(default_factory=list)
    
    # Metadata
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    node_execution_times: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary for storage"""
        return {
            "document_id": self.document_id,
            "summary": self.summary,
            "topics": self.topics,
            "entities": self.entities,
            "compliance_flags": self.compliance_flags,
            "knowledge_graph": self.knowledge_graph,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "node_execution_times": self.node_execution_times,
            "errors": self.errors
        }