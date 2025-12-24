"""
Document processing service for extracting real metadata from documents.
"""
import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    from langdetect import detect, LangDetectException
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False

try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False


class DocumentProcessor:
    """Service for processing documents and extracting metadata."""
    
    def __init__(self):
        self.nlp = None
        if SPACY_AVAILABLE:
            try:
                # Try to load spaCy model (download if needed: python -m spacy download en_core_web_sm)
                self.nlp = spacy.load("en_core_web_sm")
            except OSError:
                # Model not installed, will use regex fallback
                pass
    
    def extract_text_from_pdf(self, file_path: str) -> tuple[str, int]:
        """
        Extract text from PDF file.
        Returns: (extracted_text, page_count)
        """
        text_parts = []
        page_count = 0
        
        # Try pdfplumber first (better text extraction)
        if PDFPLUMBER_AVAILABLE:
            try:
                with pdfplumber.open(file_path) as pdf:
                    page_count = len(pdf.pages)
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text_parts.append(page_text)
                return "\n\n".join(text_parts), page_count
            except Exception as e:
                print(f"pdfplumber failed: {e}, trying pypdf")
        
        # Fallback to pypdf
        if PYPDF_AVAILABLE:
            try:
                reader = PdfReader(file_path)
                page_count = len(reader.pages)
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                return "\n\n".join(text_parts), page_count
            except Exception as e:
                print(f"pypdf failed: {e}")
        
        return "", 0
    
    def extract_text_from_image(self, file_path: str) -> str:
        """Extract text from image using OCR."""
        if not OCR_AVAILABLE:
            return ""
        
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"OCR failed: {e}")
            return ""
    
    def detect_language(self, text: str) -> str:
        """Detect language of text."""
        if not LANGDETECT_AVAILABLE or not text:
            return "en"  # Default to English
        
        try:
            return detect(text)
        except LangDetectException:
            return "en"
    
    def extract_entities(self, text: str) -> Dict[str, list]:
        """Extract useful entities (dates, amounts, companies, emails, phones, etc.) from text."""
        entities = {
            "dates": [],
            "amounts": [],
            "companies": [],
            "emails": [],
            "phone_numbers": [],
            "urls": [],
            "keywords": []
        }
        
        if not text:
            return entities
        
        # Extract dates (various formats) - more comprehensive
        date_patterns = [
            r'\b\d{4}-\d{2}-\d{2}\b',  # YYYY-MM-DD
            r'\b\d{1,2}/\d{1,2}/\d{4}\b',  # MM/DD/YYYY
            r'\b\d{1,2}-\d{1,2}-\d{4}\b',  # MM-DD-YYYY
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}\b',  # Month DD, YYYY
            r'\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{4}\b',  # DD Month YYYY
        ]
        
        for pattern in date_patterns:
            dates = re.findall(pattern, text, re.IGNORECASE)
            entities["dates"].extend(dates)
        
        # Remove duplicates and invalid dates
        entities["dates"] = sorted(list(set(entities["dates"])))[:15]
        
        # Extract amounts (currency) - more comprehensive
        amount_patterns = [
            r'\$[\d,]+\.?\d{0,2}',  # $1,234.56
            r'USD\s*[\d,]+\.?\d{0,2}',  # USD 1234.56
            r'[\d,]+\.?\d{0,2}\s*(?:dollars|USD|EUR|GBP)',  # 1234.56 dollars
            r'€[\d,]+\.?\d{0,2}',  # Euro
            r'£[\d,]+\.?\d{0,2}',  # Pound
        ]
        
        for pattern in amount_patterns:
            amounts = re.findall(pattern, text, re.IGNORECASE)
            entities["amounts"].extend(amounts)
        
        # Remove duplicates
        entities["amounts"] = sorted(list(set(entities["amounts"])))[:15]
        
        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        entities["emails"] = sorted(list(set(emails)))[:10]
        
        # Extract phone numbers
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # US format: 123-456-7890
            r'\b\(\d{3}\)\s?\d{3}[-.]?\d{4}\b',  # (123) 456-7890
            r'\b\+?\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}\b',  # International
        ]
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            entities["phone_numbers"].extend(phones)
        entities["phone_numbers"] = sorted(list(set(entities["phone_numbers"])))[:10]
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        entities["urls"] = sorted(list(set(urls)))[:10]
        
        # Extract companies/organizations - improved filtering
        if self.nlp:
            try:
                doc = self.nlp(text[:15000])  # Process more text
                orgs = []
                for ent in doc.ents:
                    if ent.label_ == "ORG":
                        org_text = ent.text.strip()
                        # Filter out common false positives
                        if len(org_text) > 2 and not org_text.upper() in ['FE', 'DNS', 'CAP', 'FS', 'SQL', 'API', 'URL', 'HTTP', 'HTTPS', 'PDF', 'XML', 'JSON', 'HTML', 'CSS', 'JS', 'AWS', 'RDS', 'RDBMS']:
                            orgs.append(org_text)
                entities["companies"] = sorted(list(set(orgs)))[:15]
            except Exception:
                pass
        
        # Fallback: Extract meaningful company names (better filtering)
        if len(entities["companies"]) < 5:
            # Look for patterns like "Company Name Inc", "Corp", "LLC", etc.
            company_patterns = [
                r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}(?:\s+(?:Inc|Corp|LLC|Ltd|Limited|Company|Co|Corporation|Technologies|Systems|Solutions|Group|Industries))\.?\b',
                r'\b(?:Amazon|Google|Microsoft|Apple|Facebook|Meta|Twitter|LinkedIn|Netflix|Uber|Airbnb|Salesforce|Oracle|IBM|Intel|NVIDIA|Adobe|PayPal|Stripe|Shopify)\b',  # Known companies
            ]
            for pattern in company_patterns:
                companies = re.findall(pattern, text, re.IGNORECASE)
                # Filter out short acronyms
                companies = [c for c in companies if len(c.split()) > 1 or len(c) > 4]
                entities["companies"].extend(companies)
            entities["companies"] = sorted(list(set(entities["companies"])))[:15]
        
        # Extract important keywords (topics, technologies, etc.)
        # Common technical/business keywords
        keyword_patterns = [
            r'\b(?:cloud|database|server|client|API|REST|GraphQL|microservices|container|docker|kubernetes|scalability|performance|security|authentication|authorization|encryption|blockchain|AI|machine learning|data science|analytics|business intelligence)\b',
        ]
        keywords = []
        for pattern in keyword_patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            keywords.extend(found)
        entities["keywords"] = sorted(list(set([k.lower() for k in keywords])))[:20]
        
        return entities
    
    def detect_document_type(self, text: str, filename: str) -> str:
        """Detect document type based on content and filename."""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # Check filename first
        if 'invoice' in filename_lower:
            return 'invoice'
        if 'receipt' in filename_lower:
            return 'receipt'
        if 'contract' in filename_lower or 'agreement' in filename_lower:
            return 'contract'
        if 'report' in filename_lower:
            return 'report'
        if 'letter' in filename_lower:
            return 'letter'
        
        # Check content
        invoice_keywords = ['invoice', 'bill to', 'amount due', 'total', 'subtotal']
        if any(keyword in text_lower for keyword in invoice_keywords):
            return 'invoice'
        
        receipt_keywords = ['receipt', 'payment received', 'thank you for your purchase']
        if any(keyword in text_lower for keyword in receipt_keywords):
            return 'receipt'
        
        contract_keywords = ['agreement', 'contract', 'terms and conditions', 'party']
        if any(keyword in text_lower for keyword in contract_keywords):
            return 'contract'
        
        return 'document'  # Default
    
    def process_document(self, file_path: str, filename: str) -> Dict[str, Any]:
        """
        Process a document and extract all metadata.
        Returns dictionary with extracted metadata.
        """
        start_time = datetime.utcnow()
        file_ext = Path(filename).suffix.lower()
        
        extracted_text = ""
        page_count = 0
        
        # Extract text based on file type
        if file_ext == '.pdf':
            extracted_text, page_count = self.extract_text_from_pdf(file_path)
        elif file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff']:
            extracted_text = self.extract_text_from_image(file_path)
            page_count = 1 if extracted_text else 0
        elif file_ext in ['.txt', '.md']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    extracted_text = f.read()
                page_count = 1
            except Exception as e:
                print(f"Error reading text file: {e}")
                extracted_text = ""
                page_count = 0
        else:
            # Try to read as text
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    extracted_text = f.read()
                page_count = 1
            except Exception:
                extracted_text = ""
                page_count = 0
        
        # Calculate word count
        words = extracted_text.split()
        word_count = len(words)
        
        # Detect language
        language = self.detect_language(extracted_text[:1000]) if extracted_text else "en"
        
        # Detect document type
        document_type = self.detect_document_type(extracted_text, filename)
        
        # Extract entities
        entities = self.extract_entities(extracted_text)
        
        # Get text preview (first 200 characters)
        text_preview = extracted_text[:200].strip() if extracted_text else ""
        if len(extracted_text) > 200:
            text_preview += "..."
        
        # Calculate processing time
        processing_time = (datetime.utcnow() - start_time).total_seconds()
        
        # Calculate additional useful metrics
        sentences = [s.strip() for s in extracted_text.split('.') if s.strip()]
        sentence_count = len(sentences)
        avg_words_per_sentence = round(word_count / sentence_count, 2) if sentence_count > 0 else 0
        
        # Extract summary (first few sentences)
        summary = '. '.join(sentences[:3]) + '.' if len(sentences) >= 3 else text_preview
        
        return {
            "page_count": page_count,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_words_per_sentence": avg_words_per_sentence,
            "language": language,
            "document_type": document_type,
            "extracted_text_preview": text_preview,
            "summary": summary[:300],  # First 300 chars of summary
            "entities": entities,
            "processing_time_seconds": round(processing_time, 2),
            "text_length": len(extracted_text),
            "has_structured_data": bool(entities.get("dates") or entities.get("amounts") or entities.get("emails")),
            "content_categories": self._categorize_content(extracted_text, entities)
        }
    
    def _categorize_content(self, text: str, entities: Dict[str, list]) -> list:
        """Categorize document content based on keywords and entities."""
        categories = []
        text_lower = text.lower()
        
        # Financial documents
        if any(kw in text_lower for kw in ['invoice', 'payment', 'bill', 'amount due', 'total', 'subtotal']):
            categories.append("financial")
        
        # Technical documents
        if any(kw in text_lower for kw in ['api', 'database', 'server', 'code', 'programming', 'software', 'architecture']):
            categories.append("technical")
        
        # Legal documents
        if any(kw in text_lower for kw in ['contract', 'agreement', 'terms', 'legal', 'party', 'obligation']):
            categories.append("legal")
        
        # Business documents
        if any(kw in text_lower for kw in ['business', 'company', 'organization', 'strategy', 'market']):
            categories.append("business")
        
        # Academic/Educational
        if any(kw in text_lower for kw in ['research', 'study', 'analysis', 'paper', 'thesis', 'university']):
            categories.append("academic")
        
        return categories

