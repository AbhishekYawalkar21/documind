from typing import List, Dict, Tuple
from app.services.llm_service import LLMService
from difflib import SequenceMatcher
import time

class QAService:
    """Question-Answering service using document chunks"""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    def find_relevant_chunks(
        self,
        query: str,
        chunks: List[Dict],
        top_k: int = 3
    ) -> List[Tuple[int, str, float]]:
        """
        Find chunks most relevant to the query
        Returns: [(chunk_id, content, similarity_score), ...]
        """
        
        query_lower = query.lower()
        scored_chunks = []
        
        for chunk in chunks:
            chunk_id = chunk.get("id")
            content = chunk.get("content", "")
            content_lower = content.lower()
            
            # Simple similarity matching
            similarity = SequenceMatcher(None, query_lower, content_lower).ratio()
            
            # Boost score for keyword matches
            for word in query_lower.split():
                if word in content_lower and len(word) > 3:
                    similarity += 0.1
            
            scored_chunks.append((chunk_id, content, similarity))
        
        # Sort by similarity
        scored_chunks.sort(key=lambda x: x[2], reverse=True)
        return scored_chunks[:top_k]
    
    def answer_question(
        self,
        question: str,
        relevant_chunks: List[str],
        document_summary: str = None
    ) -> Tuple[str, float]:
        """
        Answer a question using relevant document chunks
        
        Returns: (answer, confidence_score)
        """
        
        # Combine relevant chunks
        context = "\n\n".join(relevant_chunks[:3])
        
        if len(context) > 2000:
            context = context[:2000]
        
        prompt = f"""Answer this question based ONLY on the document.

Question: {question}

Document content:
{context}

{"Document summary: " + document_summary[:200] if document_summary else ""}

Rules:
- Answer based only on what's in the document
- If answer is not in the document, say "The document does not contain information about this."
- Be concise and clear
- Don't make up information

Answer:"""
        
        try:
            print(f"[QA] Answering: {question[:50]}...")
            start_time = time.time()
            
            answer = self.llm.call_llm(prompt)
            
            elapsed = time.time() - start_time
            print(f"[QA] Answer in {elapsed:.2f}s")
            
            # Simple confidence scoring
            confidence = min(0.95, 0.5 + (len(answer.split()) / 100))
            
            # Reduce confidence if answer says "not in document"
            if "does not contain" in answer.lower():
                confidence = 0.3
            
            return answer, confidence
        
        except Exception as e:
            print(f"[QA] Error: {str(e)}")
            return f"Error: {str(e)}", 0.0