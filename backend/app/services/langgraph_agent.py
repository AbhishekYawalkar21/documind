from app.services.llm_service import LLMService
from app.services.agent_nodes import AnalysisNodes
from app.services.agent_state import DocumentAnalysisState
from datetime import datetime
import time
import os
from dotenv import load_dotenv

load_dotenv()

class DocumentAnalysisAgent:
    """Main orchestrator for document analysis using local LLM (Ollama)"""
    
    def __init__(self):
        """Initialize agent with Ollama"""
        
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
        ollama_model = os.getenv("OLLAMA_MODEL", "mistral")
        
        print(f"\n[AGENT] Initializing with Ollama")
        print(f"[AGENT] Model: {ollama_model}")
        print(f"[AGENT] URL: {ollama_url}")
        
        self.llm = LLMService(
            ollama_url=ollama_url,
            model=ollama_model
        )
        self.nodes = AnalysisNodes(self.llm)
    
    def execute(self, document_id: str, chunks: list) -> DocumentAnalysisState:
        """
        Execute the complete analysis workflow
        
        Args:
            document_id: UUID of document
            chunks: List of text chunks
        
        Returns:
            DocumentAnalysisState with complete analysis
        """
        
        state = DocumentAnalysisState(
            document_id=document_id,
            chunks=chunks,
            started_at=datetime.utcnow()
        )
        
        print(f"\n{'='*60}")
        print(f"[AGENT] Starting document analysis")
        print(f"[AGENT] Document ID: {document_id}")
        print(f"[AGENT] Chunks: {len(chunks)}")
        print(f"[AGENT] Model: {self.llm.model}")
        print(f"{'='*60}\n")
        
        try:
            print("[NODE] 1/5 Running: summarize_node")
            state = self.nodes.summarize_node(state)
            
            print("[NODE] 2/5 Running: entity_extraction_node")
            state = self.nodes.entity_extraction_node(state)
            
            print("[NODE] 3/5 Running: compliance_check_node")
            state = self.nodes.compliance_check_node(state)
            
            print("[NODE] 4/5 Running: relationship_mapping_node")
            state = self.nodes.relationship_mapping_node(state)
            
            print("[NODE] 5/5 Running: qa_preparation_node")
            state = self.nodes.qa_preparation_node(state)
            
            if state.completed_at and state.started_at:
                total_time = (state.completed_at - state.started_at).total_seconds()
                print(f"\n[AGENT] ✅ Complete in {total_time:.2f}s")
                print(f"[AGENT] Topics: {len(state.topics)}")
                print(f"[AGENT] Entities: {sum(len(v) for v in state.entities.values())}")
                print(f"[AGENT] Flags: {len(state.compliance_flags)}")
                print(f"[AGENT] Relationships: {len(state.knowledge_graph)}")
            
            print(f"{'='*60}\n")
            
        except Exception as e:
            print(f"\n[AGENT] ❌ Analysis failed: {str(e)}")
            state.errors.append(f"Analysis failed: {str(e)}")
            raise
        
        return state