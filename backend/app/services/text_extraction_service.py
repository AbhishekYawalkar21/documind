import pypdf
import pdfplumber
from typing import Dict
import re

class TextExtractor:
    """Extract text from PDF"""
    
    @staticmethod
    def extract_text_pypdf(file_content: bytes) -> str:
        """Extract using pypdf"""
        try:
            from io import BytesIO
            pdf_file = BytesIO(file_content)
            reader = pypdf.PdfReader(pdf_file)
            
            text = ""
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
            
            return text
        except Exception as e:
            raise Exception(f"pypdf error: {str(e)}")
    
    @staticmethod
    def extract_text_pdfplumber(file_content: bytes) -> Dict:
        """Extract using pdfplumber"""
        try:
            from io import BytesIO
            pdf_file = BytesIO(file_content)
            
            result = {
                "text": "",
                "tables": [],
                "page_count": 0
            }
            
            with pdfplumber.open(pdf_file) as pdf:
                result["page_count"] = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    result["text"] += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                    
                    if page.tables:
                        result["tables"].append({
                            "page": page_num + 1,
                            "table_count": len(page.tables)
                        })
            
            return result
        except Exception as e:
            raise Exception(f"pdfplumber error: {str(e)}")
    
    @staticmethod
    def extract_all(file_content: bytes) -> Dict:
        """Extract using both methods"""
        try:
            result = TextExtractor.extract_text_pdfplumber(file_content)
            result["text"] = TextExtractor.clean_text(result["text"])
            return result
        except:
            try:
                text = TextExtractor.extract_text_pypdf(file_content)
                return {
                    "text": TextExtractor.clean_text(text),
                    "tables": [],
                    "page_count": 0,
                    "fallback": "pypdf"
                }
            except Exception as e:
                raise Exception(f"Both extraction methods failed: {str(e)}")
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean extracted text"""
        text = text.replace('\x00', '')
        text = text.replace('\r\n', '\n')
        text = text.replace('\r', '\n')
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n\n+', '\n\n', text)
        text = text.strip()
        return text