from typing import List, Dict
import tiktoken
import re

class ChunkingService:
    """Split text into semantic chunks"""
    
    def __init__(self, max_tokens: int = 800, overlap_tokens: int = 100):
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens
        try:
            self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        except:
            self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        try:
            return len(self.tokenizer.encode(text))
        except:
            return len(text) // 4  # Rough estimate
    
    def chunk_text(self, text: str, page_numbers: List[int] = None) -> List[Dict]:
        """Chunk text semantically with overlap"""
        
        if not text or text.strip() == "":
            return []
        
        paragraphs = re.split(r'\n\n+', text.strip())
        
        chunks = []
        current_chunk = ""
        current_tokens = 0
        chunk_idx = 0
        
        for para in paragraphs:
            if not para.strip():
                continue
            
            para_tokens = self.count_tokens(para)
            
            if para_tokens > self.max_tokens:
                sentences = re.split(r'(?<=[.!?])\s+', para.strip())
                
                for sentence in sentences:
                    if not sentence.strip():
                        continue
                    
                    sent_tokens = self.count_tokens(sentence)
                    
                    if sent_tokens > self.max_tokens:
                        words = sentence.split()
                        for word in words:
                            word_tokens = self.count_tokens(word)
                            
                            if current_tokens + word_tokens > self.max_tokens:
                                if current_chunk.strip():
                                    chunks.append({
                                        "chunk_index": chunk_idx,
                                        "content": current_chunk.strip(),
                                        "token_count": current_tokens,
                                        "page_number": page_numbers[0] if page_numbers else 1
                                    })
                                    chunk_idx += 1
                                
                                overlap_chars = int((self.overlap_tokens * 4))
                                overlap_text = current_chunk[-overlap_chars:] if len(current_chunk) > overlap_chars else current_chunk
                                current_chunk = overlap_text + " " + word
                                current_tokens = self.count_tokens(current_chunk)
                            else:
                                current_chunk += " " + word if current_chunk else word
                                current_tokens += word_tokens
                    else:
                        if current_tokens + sent_tokens > self.max_tokens and current_chunk.strip():
                            chunks.append({
                                "chunk_index": chunk_idx,
                                "content": current_chunk.strip(),
                                "token_count": current_tokens,
                                "page_number": page_numbers[0] if page_numbers else 1
                            })
                            chunk_idx += 1
                            
                            overlap_chars = int((self.overlap_tokens * 4))
                            overlap_text = current_chunk[-overlap_chars:] if len(current_chunk) > overlap_chars else current_chunk
                            current_chunk = overlap_text + " " + sentence
                            current_tokens = self.count_tokens(current_chunk)
                        else:
                            current_chunk += " " + sentence if current_chunk else sentence
                            current_tokens += sent_tokens
            else:
                if current_tokens + para_tokens > self.max_tokens and current_chunk.strip():
                    chunks.append({
                        "chunk_index": chunk_idx,
                        "content": current_chunk.strip(),
                        "token_count": current_tokens,
                        "page_number": page_numbers[0] if page_numbers else 1
                    })
                    chunk_idx += 1
                    
                    overlap_chars = int((self.overlap_tokens * 4))
                    overlap_text = current_chunk[-overlap_chars:] if len(current_chunk) > overlap_chars else current_chunk
                    current_chunk = overlap_text + "\n\n" + para
                    current_tokens = self.count_tokens(current_chunk)
                else:
                    current_chunk += "\n\n" + para if current_chunk else para
                    current_tokens += para_tokens
        
        if current_chunk.strip():
            chunks.append({
                "chunk_index": chunk_idx,
                "content": current_chunk.strip(),
                "token_count": self.count_tokens(current_chunk.strip()),
                "page_number": page_numbers[0] if page_numbers else 1
            })
        
        return chunks