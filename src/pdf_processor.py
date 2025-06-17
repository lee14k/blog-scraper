import re
import io
import tempfile
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse, parse_qs
from datetime import datetime
from pathlib import Path

import requests
import PyPDF2
from PyPDF2 import PdfReader

from .base_scraper import BaseScraper
from .models import KnowledgebaseEntry, ScrapingResult, Author, Tag


class PDFProcessor(BaseScraper):
    """Processor for PDF documents, including Google Drive links"""
    
    def __init__(self, config=None):
        super().__init__(config)
        
    def scrape_google_drive_pdf(self, drive_url: str, max_chapters: int = 8) -> ScrapingResult:
        """Scrape PDF from Google Drive link"""
        result = ScrapingResult(success=False, source_url=drive_url)
        
        try:
            # Convert Google Drive sharing URL to direct download URL
            download_url = self._convert_drive_url(drive_url)
            if not download_url:
                result.errors.append("Could not convert Google Drive URL to download URL")
                return result
                
            # Download the PDF
            pdf_content = self._download_pdf(download_url)
            if not pdf_content:
                result.errors.append("Failed to download PDF")
                return result
                
            # Process the PDF
            entries = self._extract_chapters_from_pdf(pdf_content, max_chapters, drive_url)
            result.entries = entries
            result.total_found = len(entries)
            result.total_scraped = len(entries)
            result.success = len(entries) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to process PDF: {e}")
            result.errors.append(f"Failed to process PDF: {str(e)}")
            
        return result
        
    def scrape_local_pdf(self, file_path: str, max_chapters: int = 8) -> ScrapingResult:
        """Scrape PDF from local file"""
        result = ScrapingResult(success=False, source_url=f"file://{file_path}")
        
        try:
            with open(file_path, 'rb') as file:
                pdf_content = file.read()
                
            entries = self._extract_chapters_from_pdf(pdf_content, max_chapters, f"file://{file_path}")
            result.entries = entries
            result.total_found = len(entries)
            result.total_scraped = len(entries)
            result.success = len(entries) > 0
            
        except Exception as e:
            self.logger.error(f"Failed to process local PDF: {e}")
            result.errors.append(f"Failed to process local PDF: {str(e)}")
            
        return result
        
    def _convert_drive_url(self, drive_url: str) -> Optional[str]:
        """Convert Google Drive sharing URL to direct download URL"""
        try:
            # Extract file ID from various Google Drive URL formats
            file_id = None
            
            if 'drive.google.com' in drive_url:
                # Format: https://drive.google.com/file/d/FILE_ID/view
                if '/file/d/' in drive_url:
                    file_id = drive_url.split('/file/d/')[1].split('/')[0]
                # Format: https://drive.google.com/open?id=FILE_ID
                elif 'open?id=' in drive_url:
                    file_id = parse_qs(urlparse(drive_url).query).get('id', [None])[0]
                # Format: https://drive.google.com/uc?id=FILE_ID
                elif 'uc?id=' in drive_url:
                    file_id = parse_qs(urlparse(drive_url).query).get('id', [None])[0]
                    
            if file_id:
                # Convert to direct download URL
                return f"https://drive.google.com/uc?export=download&id={file_id}"
                
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to convert Drive URL: {e}")
            return None
            
    def _download_pdf(self, url: str) -> Optional[bytes]:
        """Download PDF content from URL"""
        try:
            # For Google Drive, we might need to handle the "virus scan warning" page
            response = self._make_request(url)
            if not response:
                return None
                
            # Check if we got the virus scan warning page
            if 'Google Drive - Virus scan warning' in response.text:
                # Extract the actual download URL from the warning page
                download_link_match = re.search(r'href="(/uc\?export=download[^"]+)"', response.text)
                if download_link_match:
                    actual_download_url = 'https://drive.google.com' + download_link_match.group(1)
                    actual_download_url = actual_download_url.replace('&amp;', '&')
                    response = self._make_request(actual_download_url)
                    
            if response and response.content:
                # Verify it's actually a PDF
                if response.content.startswith(b'%PDF'):
                    return response.content
                else:
                    self.logger.warning("Downloaded content is not a valid PDF")
                    
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to download PDF: {e}")
            return None
            
    def _extract_chapters_from_pdf(self, pdf_content: bytes, max_chapters: int, source_url: str) -> List[KnowledgebaseEntry]:
        """Extract chapters from PDF content"""
        entries = []
        
        try:
            # Create a file-like object from bytes
            pdf_file = io.BytesIO(pdf_content)
            reader = PdfReader(pdf_file)
            
            total_pages = len(reader.pages)
            self.logger.info(f"PDF has {total_pages} pages")
            
            # Try to detect chapter breaks
            chapters = self._detect_chapters(reader, max_chapters)
            
            if not chapters:
                # Fallback: split by page ranges if no chapters detected
                pages_per_chapter = max(1, total_pages // max_chapters)
                chapters = []
                for i in range(0, min(total_pages, max_chapters * pages_per_chapter), pages_per_chapter):
                    end_page = min(i + pages_per_chapter - 1, total_pages - 1)
                    chapters.append({
                        'title': f"Chapter {len(chapters) + 1}",
                        'start_page': i,
                        'end_page': end_page
                    })
                    
            # Extract content for each chapter
            for chapter in chapters[:max_chapters]:
                try:
                    content = self._extract_chapter_content(reader, chapter)
                    if content and len(content.strip()) > 100:  # Minimum content length
                        entry = KnowledgebaseEntry(
                            id=self._generate_id(source_url, chapter['title']),
                            title=chapter['title'],
                            url=source_url,
                            source_domain=urlparse(source_url).netloc or "local",
                            content=content,
                            content_type="pdf_chapter",
                            metadata={
                                "start_page": chapter['start_page'],
                                "end_page": chapter['end_page'],
                                "total_pages": total_pages,
                                "chapter_number": len(entries) + 1
                            }
                        )
                        entries.append(entry)
                        
                except Exception as e:
                    self.logger.error(f"Failed to extract chapter {chapter['title']}: {e}")
                    
        except Exception as e:
            self.logger.error(f"Failed to process PDF: {e}")
            
        return entries
        
    def _detect_chapters(self, reader: PdfReader, max_chapters: int) -> List[Dict[str, Any]]:
        """Try to detect chapter boundaries in the PDF"""
        chapters = []
        
        try:
            # Look for outline/bookmarks first
            if reader.outline:
                for bookmark in reader.outline:
                    if len(chapters) >= max_chapters:
                        break
                        
                    if hasattr(bookmark, 'title') and hasattr(bookmark, 'page'):
                        try:
                            page_num = reader.get_destination_page_number(bookmark)
                            chapters.append({
                                'title': str(bookmark.title),
                                'start_page': page_num
                            })
                        except:
                            continue
                            
                # Set end pages
                for i in range(len(chapters)):
                    if i < len(chapters) - 1:
                        chapters[i]['end_page'] = chapters[i + 1]['start_page'] - 1
                    else:
                        chapters[i]['end_page'] = len(reader.pages) - 1
                        
                return chapters
                
            # Fallback: look for chapter headings in text
            chapter_patterns = [
                r'^Chapter\s+\d+',
                r'^CHAPTER\s+\d+',
                r'^\d+\.\s+[A-Z][A-Za-z\s]+',
                r'^[A-Z][A-Z\s]+$'  # All caps headings
            ]
            
            for page_num, page in enumerate(reader.pages):
                if len(chapters) >= max_chapters:
                    break
                    
                try:
                    text = page.extract_text()
                    lines = text.split('\n')
                    
                    for line in lines[:10]:  # Check first 10 lines of each page
                        line = line.strip()
                        if len(line) > 5 and len(line) < 100:  # Reasonable title length
                            for pattern in chapter_patterns:
                                if re.match(pattern, line, re.IGNORECASE):
                                    # Close previous chapter
                                    if chapters:
                                        chapters[-1]['end_page'] = page_num - 1
                                        
                                    chapters.append({
                                        'title': line,
                                        'start_page': page_num
                                    })
                                    break
                                    
                except Exception as e:
                    self.logger.debug(f"Error processing page {page_num}: {e}")
                    continue
                    
            # Set end page for last chapter
            if chapters:
                chapters[-1]['end_page'] = len(reader.pages) - 1
                
        except Exception as e:
            self.logger.error(f"Failed to detect chapters: {e}")
            
        return chapters
        
    def _extract_chapter_content(self, reader: PdfReader, chapter: Dict[str, Any]) -> str:
        """Extract text content from a chapter"""
        content_parts = []
        
        try:
            start_page = chapter['start_page']
            end_page = chapter['end_page']
            
            for page_num in range(start_page, min(end_page + 1, len(reader.pages))):
                try:
                    page = reader.pages[page_num]
                    text = page.extract_text()
                    
                    # Clean up the text
                    text = self._clean_pdf_text(text)
                    
                    if text:
                        content_parts.append(text)
                        
                except Exception as e:
                    self.logger.debug(f"Error extracting text from page {page_num}: {e}")
                    continue
                    
            return '\n\n'.join(content_parts)
            
        except Exception as e:
            self.logger.error(f"Failed to extract chapter content: {e}")
            return ""
            
    def _clean_pdf_text(self, text: str) -> str:
        """Clean and format text extracted from PDF"""
        if not text:
            return ""
            
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Fix line breaks that split words
        text = re.sub(r'(\w)-\s+(\w)', r'\1\2', text)
        
        # Add proper paragraph breaks
        text = re.sub(r'\.(\s+)([A-Z])', r'.\n\n\2', text)
        
        return text.strip()
        
    def scrape(self, url: str) -> ScrapingResult:
        """Main scrape method for PDFs"""
        if url.startswith('file://'):
            file_path = url[7:]  # Remove 'file://' prefix
            return self.scrape_local_pdf(file_path)
        else:
            return self.scrape_google_drive_pdf(url) 