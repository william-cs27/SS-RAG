"""
PDF Parser for IPC Sunday School Curriculum
Extracts text and metadata from textbooks with lesson-based structure
"""

import pymupdf
import re
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class DocumentChunk:
    """Represents a chunk of text with metadata"""
    text: str
    metadata: Dict[str, Any]
    page_number: int


class IPCPDFParser:
    """Parser specifically designed for IPC Sunday School textbooks"""
    
    def __init__(self):
        # Common patterns in IPC textbooks
        self.lesson_pattern = re.compile(r'Lesson\s+(\d+)[:\s]*(.+?)(?:\n|$)', re.IGNORECASE)
        self.verse_pattern = re.compile(r'(?:Memory\s+Verse|Bible\s+Verse)[:\s]*(.+?)(?:\n\n|\n[A-Z]|$)', 
                                       re.IGNORECASE | re.DOTALL)
        self.grade_pattern = re.compile(r'Grade\s+(\d+)', re.IGNORECASE)
        
    def extract_metadata_from_filename(self, filename: str) -> Dict[str, Any]:
        """Extract metadata from PDF filename"""
        metadata = {
            'source_file': filename,
            'curriculum': 'unknown',
            'grade': None,
            'doc_type': 'textbook'
        }
        
        filename_lower = filename.lower()
        
        # Detect curriculum
        if 'ipc' in filename_lower:
            metadata['curriculum'] = 'IPC'
        elif 'radiant' in filename_lower:
            metadata['curriculum'] = 'Radiant Life'
        elif 'christian identity' in filename_lower or 'mci' in filename_lower:
            metadata['curriculum'] = 'Christian Identity'
            
        # Detect document type
        if 'teacher' in filename_lower:
            metadata['doc_type'] = 'teacher_guide'
        elif 'student' in filename_lower:
            metadata['doc_type'] = 'student_guide'
            
        # Extract grade
        grade_match = self.grade_pattern.search(filename)
        if grade_match:
            metadata['grade'] = int(grade_match.group(1))
            
        return metadata
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Extract text and metadata from PDF, page by page"""
        pages_data = []
        
        try:
            doc = pymupdf.open(pdf_path)
            
            for page_num, page in enumerate(doc, start=1):
                text = page.get_text()
                
                # Skip empty pages
                if not text.strip():
                    continue
                    
                pages_data.append({
                    'page_number': page_num,
                    'text': text,
                    'char_count': len(text)
                })
                
            doc.close()
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {e}")
            
        return pages_data
    
    def identify_lesson_boundaries(self, text: str) -> List[Dict[str, Any]]:
        """Identify lesson numbers and titles in text"""
        lessons = []
        
        for match in self.lesson_pattern.finditer(text):
            lesson_num = int(match.group(1))
            lesson_title = match.group(2).strip()
            
            lessons.append({
                'lesson_number': lesson_num,
                'lesson_title': lesson_title,
                'start_pos': match.start()
            })
            
        return lessons
    
    def extract_memory_verses(self, text: str) -> List[str]:
        """Extract memory verses from text"""
        verses = []
        
        for match in self.verse_pattern.finditer(text):
            verse_text = match.group(1).strip()
            if len(verse_text) > 10:  # Filter out false positives
                verses.append(verse_text)
                
        return verses
    
    def chunk_by_lessons(self, pages_data: List[Dict], 
                        base_metadata: Dict,
                        chunk_size: int = 600,
                        chunk_overlap: int = 100) -> List[DocumentChunk]:
        """Chunk text by lesson boundaries when possible, otherwise by size"""
        
        chunks = []
        
        # Combine all pages into single text for lesson detection
        full_text = "\n\n".join([p['text'] for p in pages_data])
        lessons = self.identify_lesson_boundaries(full_text)
        
        if not lessons:
            # No lessons detected, fall back to page-by-page chunking
            return self._chunk_by_pages(pages_data, base_metadata, chunk_size, chunk_overlap)
        
        # Split text by lessons
        for i, lesson in enumerate(lessons):
            lesson_start = lesson['start_pos']
            lesson_end = lessons[i + 1]['start_pos'] if i + 1 < len(lessons) else len(full_text)
            
            lesson_text = full_text[lesson_start:lesson_end]
            
            # Extract verses from this lesson
            verses = self.extract_memory_verses(lesson_text)
            
            # Check if lesson is too long and needs sub-chunking
            if len(lesson_text) > chunk_size * 2:
                sub_chunks = self._split_text(lesson_text, chunk_size, chunk_overlap)
                
                for sub_idx, sub_text in enumerate(sub_chunks):
                    chunk_metadata = {
                        **base_metadata,
                        'lesson_number': lesson['lesson_number'],
                        'lesson_title': lesson['lesson_title'],
                        'sub_chunk': sub_idx + 1,
                        'contains_verse': len(verses) > 0,
                        'exam_relevant': True  # Assume all lessons are exam relevant
                    }
                    
                    chunks.append(DocumentChunk(
                        text=sub_text,
                        metadata=chunk_metadata,
                        page_number=0  # Page number tracked separately
                    ))
            else:
                chunk_metadata = {
                    **base_metadata,
                    'lesson_number': lesson['lesson_number'],
                    'lesson_title': lesson['lesson_title'],
                    'contains_verse': len(verses) > 0,
                    'exam_relevant': True
                }
                
                chunks.append(DocumentChunk(
                    text=lesson_text,
                    metadata=chunk_metadata,
                    page_number=0
                ))
        
        return chunks
    
    def _chunk_by_pages(self, pages_data: List[Dict],
                       base_metadata: Dict,
                       chunk_size: int,
                       chunk_overlap: int) -> List[DocumentChunk]:
        """Fallback chunking by pages when lessons aren't detected"""
        
        chunks = []
        
        for page in pages_data:
            text = page['text']
            
            if len(text) <= chunk_size:
                chunk_metadata = {
                    **base_metadata,
                    'page_number': page['page_number']
                }
                
                chunks.append(DocumentChunk(
                    text=text,
                    metadata=chunk_metadata,
                    page_number=page['page_number']
                ))
            else:
                sub_chunks = self._split_text(text, chunk_size, chunk_overlap)
                
                for sub_idx, sub_text in enumerate(sub_chunks):
                    chunk_metadata = {
                        **base_metadata,
                        'page_number': page['page_number'],
                        'sub_chunk': sub_idx + 1
                    }
                    
                    chunks.append(DocumentChunk(
                        text=sub_text,
                        metadata=chunk_metadata,
                        page_number=page['page_number']
                    ))
        
        return chunks
    
    def _split_text(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Split text into chunks with overlap"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for period + space within last 100 chars
                last_period = text.rfind('. ', end - 100, end)
                if last_period > start:
                    end = last_period + 1
            
            chunks.append(text[start:end].strip())
            start = end - overlap
            
        return chunks
    
    def parse_pdf(self, pdf_path: str, chunk_size: int = 600, 
                 chunk_overlap: int = 100) -> List[DocumentChunk]:
        """Main method to parse a PDF and return chunks"""
        
        # Extract base metadata from filename
        base_metadata = self.extract_metadata_from_filename(Path(pdf_path).name)
        
        # Extract text from PDF
        pages_data = self.extract_text_from_pdf(pdf_path)
        
        if not pages_data:
            print(f"No text extracted from {pdf_path}")
            return []
        
        # Chunk the text
        chunks = self.chunk_by_lessons(pages_data, base_metadata, chunk_size, chunk_overlap)
        
        print(f"Processed {pdf_path}: {len(pages_data)} pages → {len(chunks)} chunks")
        
        return chunks
