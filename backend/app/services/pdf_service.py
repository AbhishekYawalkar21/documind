from typing import Dict, Tuple
from datetime import datetime

class PDFValidator:
    """Validate PDF files"""
    
    MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB
    ALLOWED_MIMETYPES = ["application/pdf"]
    
    @staticmethod
    def validate(file_content: bytes, filename: str, mime_type: str) -> Tuple[bool, str]:
        """Validate file - Returns (is_valid, error_message)"""
        
        if len(file_content) > PDFValidator.MAX_FILE_SIZE_BYTES:
            return False, f"File too large. Max: 50MB"
        
        if not filename.lower().endswith('.pdf'):
            return False, "Only PDF files allowed"
        
        if mime_type not in PDFValidator.ALLOWED_MIMETYPES:
            return False, f"Invalid MIME type"
        
        if not file_content.startswith(b'%PDF'):
            return False, "File is not a valid PDF"
        
        return True, ""

class PDFMetadataExtractor:
    """Extract basic metadata from PDF"""
    
    @staticmethod
    def extract_basic_metadata(file_content: bytes) -> Dict:
        """Extract basic metadata"""
        try:
            version = file_content[:10].decode('utf-8', errors='ignore')
            
            return {
                "version": version.strip(),
                "file_size_bytes": len(file_content),
                "extracted_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                "error": str(e),
                "file_size_bytes": len(file_content),
                "extracted_at": datetime.utcnow().isoformat()
            }