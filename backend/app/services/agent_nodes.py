import json
import time
from typing import Dict
from app.services.llm_service import LLMService
from app.services.agent_state import DocumentAnalysisState
from datetime import datetime

class AnalysisNodes:
    """Individual nodes for LangGraph agent - optimized for Ollama"""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    def summarize_node(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """Node 1: Summarize document"""
        
        start_time = time.time()
        
        try:
            chunks_to_summarize = state.chunks[:5]
            context = "\n\n".join(chunks_to_summarize)
            
            if len(context) > 3000:
                context = context[:3000]
            
            prompt = f"""Read this document and provide:
1. A clear 3-5 sentence summary
2. Main topics (list 3-5 topics)

CRITICAL: If you use quotes inside your text summary descriptions, you MUST use single quotes (') instead of double quotes (\"). Double quotes will break the JSON parsing pipeline.

Document:
{context}

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "summary": "Your summary here",
  "topics": ["topic1", "topic2"]
}}"""
            
            response_text = self.llm.call_llm_json(prompt)
            response = json.loads(response_text)
            
            state.summary = response.get("summary", "")
            state.topics = response.get("topics", [])
            state.analysis_step = "summarize_complete"
            
            print(f"  ✅ Summary: {len(state.summary)} chars")
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing error: {str(e)}"
            state.errors.append(error_msg)
            state.summary = "Could not generate summary"
            print(f"  ⚠️  {error_msg}")
        except Exception as e:
            error_msg = f"Error in summarize: {str(e)}"
            state.errors.append(error_msg)
            print(f"  ⚠️  {error_msg}")
        
        execution_time = time.time() - start_time
        state.node_execution_times["summarize"] = execution_time
        
        return state
    
    def entity_extraction_node(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """Node 2: Extract entities"""
        
        start_time = time.time()
        
        try:
            context = "\n\n".join(state.chunks[:10])
            
            if len(context) > 4000:
                context = context[:4000]
            
            prompt = f"""Extract named entities from this document.

Document:
{context}

Find and list:
- Dates (YYYY-MM-DD format if possible)
- Person names
- Organizations
- Amounts (with currency)
- Email addresses
- Phone numbers
- Locations

Only include entities you actually found. Leave empty arrays for nothing.

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "dates": [],
  "names": [],
  "organizations": [],
  "amounts": [],
  "emails": [],
  "phone_numbers": [],
  "locations": []
}}"""
            
            response_text = self.llm.call_llm_json(prompt)
            response = json.loads(response_text)
            
            state.entities = response
            state.analysis_step = "entity_extraction_complete"
            
            total_entities = sum(len(v) for v in response.values())
            print(f"  ✅ Extracted: {total_entities} entities")
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing error: {str(e)}"
            state.errors.append(error_msg)
            state.entities = {}
            print(f"  ⚠️  {error_msg}")
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            state.errors.append(error_msg)
            print(f"  ⚠️  {error_msg}")
        
        execution_time = time.time() - start_time
        state.node_execution_times["entity_extraction"] = execution_time
        
        return state
    
    def compliance_check_node(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """Node 3: Check compliance issues"""
        
        start_time = time.time()
        
        try:
            context = "\n\n".join(state.chunks[:8])
            
            if len(context) > 3000:
                context = context[:3000]
            
            entities_str = json.dumps(state.entities, indent=2)
            
            prompt = f"""Check for compliance and security issues.

Document:
{context}

Entities found:
{entities_str}

Look for:
1. GDPR: Personal data without consent
2. Missing signatures
3. Hardcoded secrets or passwords
4. Missing dates or amounts
5. Missing legal disclaimer

Only include issues you actually find.

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "flags": [
    {{
      "type": "GDPR_PII",
      "severity": "high",
      "description": "Email found without consent",
      "location": "Line 5"
    }}
  ]
}}"""
            
            response_text = self.llm.call_llm_json(prompt)
            response = json.loads(response_text)
            
            state.compliance_flags = response.get("flags", [])
            state.analysis_step = "compliance_check_complete"
            
            print(f"  ✅ Compliance: {len(state.compliance_flags)} issues")
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing error: {str(e)}"
            state.errors.append(error_msg)
            state.compliance_flags = []
            print(f"  ⚠️  {error_msg}")
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            state.errors.append(error_msg)
            print(f"  ⚠️  {error_msg}")
        
        execution_time = time.time() - start_time
        state.node_execution_times["compliance_check"] = execution_time
        
        return state
    
    def relationship_mapping_node(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """Node 4: Extract relationships"""
        
        start_time = time.time()
        
        try:
            entities_str = json.dumps(state.entities, indent=2)
            summary = state.summary[:500] if state.summary else ""
            
            prompt = f"""Extract relationships between entities.

Summary: {summary}

Entities:
{entities_str}

Find relationships like:
- Person X works at Company Y
- Person X signed with Person Y
- Company X owns Company Y

Only include relationships you can infer.

Respond ONLY with valid JSON (no markdown, no extra text):
{{
  "relationships": [
    {{
      "entity1": "John Smith",
      "relation": "works_at",
      "entity2": "Acme Corp"
    }}
  ]
}}"""
            
            response_text = self.llm.call_llm_json(prompt)
            response = json.loads(response_text)
            
            state.knowledge_graph = response.get("relationships", [])
            state.analysis_step = "relationship_mapping_complete"
            
            print(f"  ✅ Relationships: {len(state.knowledge_graph)}")
            
        except json.JSONDecodeError as e:
            error_msg = f"JSON parsing error: {str(e)}"
            state.errors.append(error_msg)
            state.knowledge_graph = []
            print(f"  ⚠️  {error_msg}")
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            state.errors.append(error_msg)
            print(f"  ⚠️  {error_msg}")
        
        execution_time = time.time() - start_time
        state.node_execution_times["relationship_mapping"] = execution_time
        
        return state
    
    def qa_preparation_node(self, state: DocumentAnalysisState) -> DocumentAnalysisState:
        """Node 5: Prepare Q&A"""
        
        start_time = time.time()
        
        try:
            state.completed_at = datetime.utcnow()
            state.analysis_step = "analysis_complete"
            print(f"  ✅ Analysis complete")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            state.errors.append(error_msg)
            print(f"  ⚠️  {error_msg}")
        
        execution_time = time.time() - start_time
        state.node_execution_times["qa_preparation"] = execution_time
        
        return state