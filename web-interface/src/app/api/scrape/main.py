import sys
import os
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
import logging

# Since we're running from project root, we can import directly from src
sys.path.insert(0, "src")

try:
    from src.scraper_manager import ScraperManager
    from src.models import ScrapingConfig, ScrapingResult, KnowledgebaseEntry
    from src.nilmamano_scraper import NilMamanoScraper
    from src.interviewing_io_scraper import InterviewingIOScraper
    from src.generic_blog_scraper import GenericBlogScraper
    from src.pdf_processor import PDFProcessor
    
    print("All scrapers imported successfully!")
    
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    raise

# Initialize FastAPI app
app = FastAPI(
    title="Blog Scraper API",
    description="API for scraping various blog sources and processing PDFs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Request/Response models
class ScrapeRequest(BaseModel):
    url: Optional[HttpUrl] = None
    config: Optional[Dict] = None

class GenericBlogRequest(BaseModel):
    blog_url: HttpUrl
    config: Optional[Dict] = None

class PDFRequest(BaseModel):
    pdf_url_or_path: str
    max_chapters: int = 8
    config: Optional[Dict] = None

class ScrapeAllRequest(BaseModel):
    google_drive_pdf_url: Optional[HttpUrl] = None
    config: Optional[Dict] = None

# Helper function to create scraping config
def create_config(config_dict: Optional[Dict] = None) -> ScrapingConfig:
    if config_dict:
        return ScrapingConfig(**config_dict)
    return ScrapingConfig()

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Blog Scraper API",
        "version": "1.0.0",
        "endpoints": {
            "/scrape/nilmamano": "Scrape DS&A posts from nilmamano.com",
            "/scrape/interviewing-io/blog": "Scrape blog posts from interviewing.io",
            "/scrape/interviewing-io/company-guides": "Scrape company guides from interviewing.io",
            "/scrape/interviewing-io/interview-guides": "Scrape interview guides from interviewing.io",
            "/scrape/interviewing-io/all": "Scrape all content from interviewing.io",
            "/scrape/generic-blog": "Scrape any generic blog",
            "/scrape/pdf": "Process PDF from URL or path",
            "/scrape/all": "Scrape all predefined sources"
        }
    }

@app.post("/scrape/nilmamano", response_model=ScrapingResult)
async def scrape_nilmamano(request: ScrapeRequest):
    """Scrape DS&A posts from nilmamano.com"""
    try:
        config = create_config(request.config)
        url = str(request.url) if request.url else "https://nilmamano.com/blog/category/dsa"
        
        with NilMamanoScraper(config) as scraper:
            result = scraper.scrape_dsa_posts(url)
            
        logger.info(f"Nilmamano scrape completed: {result.total_scraped} entries")
        return result
        
    except Exception as e:
        logger.error(f"Failed to scrape nilmamano: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/interviewing-io/blog", response_model=ScrapingResult)
async def scrape_interviewing_io_blog(request: ScrapeRequest):
    """Scrape blog posts from interviewing.io"""
    try:
        config = create_config(request.config)
        url = str(request.url) if request.url else "https://interviewing.io/blog"
        
        with InterviewingIOScraper(config) as scraper:
            result = scraper.scrape_blog(url)
            
        logger.info(f"Interviewing.io blog scrape completed: {result.total_scraped} entries")
        return result
        
    except Exception as e:
        logger.error(f"Failed to scrape interviewing.io blog: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/interviewing-io/company-guides", response_model=ScrapingResult)
async def scrape_interviewing_io_company_guides(request: ScrapeRequest):
    """Scrape company guides from interviewing.io"""
    try:
        config = create_config(request.config)
        url = str(request.url) if request.url else "https://interviewing.io/topics#companies"
        
        with InterviewingIOScraper(config) as scraper:
            result = scraper.scrape_company_guides(url)
            
        logger.info(f"Interviewing.io company guides scrape completed: {result.total_scraped} entries")
        return result
        
    except Exception as e:
        logger.error(f"Failed to scrape interviewing.io company guides: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/interviewing-io/interview-guides", response_model=ScrapingResult)
async def scrape_interviewing_io_interview_guides(request: ScrapeRequest):
    """Scrape interview guides from interviewing.io"""
    try:
        config = create_config(request.config)
        url = str(request.url) if request.url else "https://interviewing.io/learn#interview-guides"
        
        with InterviewingIOScraper(config) as scraper:
            result = scraper.scrape_interview_guides(url)
            
        logger.info(f"Interviewing.io interview guides scrape completed: {result.total_scraped} entries")
        return result
        
    except Exception as e:
        logger.error(f"Failed to scrape interviewing.io interview guides: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/interviewing-io/all", response_model=List[ScrapingResult])
async def scrape_interviewing_io_all(request: ScrapeRequest):
    """Scrape all content from interviewing.io (blog, company guides, interview guides)"""
    try:
        config = create_config(request.config)
        
        with InterviewingIOScraper(config) as scraper:
            results = scraper.scrape_all()
            
        total_scraped = sum(result.total_scraped for result in results)
        logger.info(f"Interviewing.io all content scrape completed: {total_scraped} total entries")
        return results
        
    except Exception as e:
        logger.error(f"Failed to scrape all interviewing.io content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/generic-blog", response_model=ScrapingResult)
async def scrape_generic_blog(request: GenericBlogRequest):
    """Scrape any generic blog"""
    try:
        config = create_config(request.config)
        
        with GenericBlogScraper(config) as scraper:
            result = scraper.scrape_blog(str(request.blog_url))
            
        logger.info(f"Generic blog scrape completed: {result.total_scraped} entries")
        return result
        
    except Exception as e:
        logger.error(f"Failed to scrape generic blog: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/pdf", response_model=ScrapingResult)
async def scrape_pdf(request: PDFRequest):
    """Process PDF from URL or local path"""
    try:
        config = create_config(request.config)
        
        with PDFProcessor(config) as processor:
            if request.pdf_url_or_path.startswith('http'):
                result = processor.scrape_google_drive_pdf(request.pdf_url_or_path, request.max_chapters)
            else:
                result = processor.scrape_local_pdf(request.pdf_url_or_path, request.max_chapters)
                
        logger.info(f"PDF processing completed: {result.total_scraped} chapters")
        return result
        
    except Exception as e:
        logger.error(f"Failed to process PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/scrape/all", response_model=Dict[str, ScrapingResult])
async def scrape_all_sources(request: ScrapeAllRequest):
    """Scrape all predefined sources"""
    try:
        config = create_config(request.config)
        manager = ScraperManager(config)
        
        google_drive_url = str(request.google_drive_pdf_url) if request.google_drive_pdf_url else None
        results = manager.scrape_all_sources(google_drive_url)
        
        total_scraped = sum(result.total_scraped for result in results.values())
        logger.info(f"All sources scrape completed: {total_scraped} total entries")
        return results
        
    except Exception as e:
        logger.error(f"Failed to scrape all sources: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Background task endpoints for long-running operations
@app.post("/scrape/all/background")
async def scrape_all_sources_background(request: ScrapeAllRequest, background_tasks: BackgroundTasks):
    """Start scraping all sources in the background"""
    
    def run_scraping():
        try:
            config = create_config(request.config)
            manager = ScraperManager(config)
            
            google_drive_url = str(request.google_drive_pdf_url) if request.google_drive_pdf_url else None
            results = manager.scrape_all_sources(google_drive_url)
            
            # Save results automatically
            manager.save_results(results)
            logger.info("Background scraping completed and results saved")
            
        except Exception as e:
            logger.error(f"Background scraping failed: {e}")
    
    background_tasks.add_task(run_scraping)
    return {"message": "Scraping started in background. Results will be saved to output directory."}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "blog-scraper-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
