from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, HttpUrl, Field


class Author(BaseModel):
    """Author information"""
    name: str
    email: Optional[str] = None
    url: Optional[HttpUrl] = None


class Tag(BaseModel):
    """Content tag/category"""
    name: str
    slug: str


class KnowledgebaseEntry(BaseModel):
    """Standard format for all scraped content"""
    # Core identification
    id: str = Field(description="Unique identifier for this entry")
    title: str
    url: HttpUrl
    source_domain: str
    
    # Content
    content: str = Field(description="Main text content in markdown format")
    excerpt: Optional[str] = None
    content_type: str = Field(description="Type: blog_post, guide, tutorial, pdf_chapter, etc.")
    
    # Metadata
    published_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    author: Optional[Author] = None
    tags: List[Tag] = []
    
    # Scraping metadata
    scraped_at: datetime = Field(default_factory=datetime.now)
    scraper_version: str = "1.0.0"
    
    # Additional structured data
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScrapingResult(BaseModel):
    """Result of a scraping operation"""
    success: bool
    entries: List[KnowledgebaseEntry] = []
    errors: List[str] = []
    total_found: int = 0
    total_scraped: int = 0
    source_url: str
    
    
class ScrapingConfig(BaseModel):
    """Configuration for scraping operations"""
    # Request settings
    delay_between_requests: float = 1.0
    max_retries: int = 3
    timeout: int = 30
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    
    # Content extraction settings
    max_content_length: int = 100000
    include_images: bool = False
    convert_to_markdown: bool = True
    
    # Output settings
    output_format: str = "json"  # json, csv, markdown
    save_raw_html: bool = False 