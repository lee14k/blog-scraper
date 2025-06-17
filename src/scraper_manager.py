import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from .models import ScrapingConfig, ScrapingResult, KnowledgebaseEntry
from .interviewing_io_scraper import InterviewingIOScraper
from .nilmamano_scraper import NilMamanoScraper
from .generic_blog_scraper import GenericBlogScraper
from .pdf_processor import PDFProcessor


class ScraperManager:
    """Main manager class that orchestrates all scrapers"""
    
    def __init__(self, config: ScrapingConfig = None):
        self.config = config or ScrapingConfig()
        self.logger = logging.getLogger(__name__)
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
    def scrape_all_sources(self, google_drive_pdf_url: str = None) -> Dict[str, ScrapingResult]:
        """Scrape all predefined sources"""
        results = {}
        
        # 1. Scrape interviewing.io
        self.logger.info("Starting interviewing.io scrape...")
        try:
            with InterviewingIOScraper(self.config) as interviewing_scraper:
                interviewing_results = interviewing_scraper.scrape_all()
                results['interviewing_io_blog'] = interviewing_results[0]
                results['interviewing_io_company_guides'] = interviewing_results[1]
                results['interviewing_io_interview_guides'] = interviewing_results[2]
        except Exception as e:
            self.logger.error(f"Failed to scrape interviewing.io: {e}")
            
        # 2. Scrape Nil's DSA blog posts
        self.logger.info("Starting nilmamano.com DSA posts scrape...")
        try:
            with NilMamanoScraper(self.config) as nil_scraper:
                results['nilmamano_dsa'] = nil_scraper.scrape_dsa_posts()
        except Exception as e:
            self.logger.error(f"Failed to scrape nilmamano.com: {e}")
            
        # 3. Process PDF if URL provided
        if google_drive_pdf_url:
            self.logger.info("Processing PDF from Google Drive...")
            try:
                with PDFProcessor(self.config) as pdf_processor:
                    results['pdf_chapters'] = pdf_processor.scrape_google_drive_pdf(google_drive_pdf_url, max_chapters=8)
            except Exception as e:
                self.logger.error(f"Failed to process PDF: {e}")
                
        return results
        
    def scrape_generic_blog(self, blog_url: str) -> ScrapingResult:
        """Scrape any generic blog"""
        self.logger.info(f"Scraping generic blog: {blog_url}")
        try:
            with GenericBlogScraper(self.config) as generic_scraper:
                return generic_scraper.scrape_blog(blog_url)
        except Exception as e:
            self.logger.error(f"Failed to scrape generic blog {blog_url}: {e}")
            return ScrapingResult(success=False, source_url=blog_url, errors=[str(e)])
            
    def scrape_pdf(self, pdf_url_or_path: str, max_chapters: int = 8) -> ScrapingResult:
        """Scrape PDF from URL or local path"""
        self.logger.info(f"Processing PDF: {pdf_url_or_path}")
        try:
            with PDFProcessor(self.config) as pdf_processor:
                if pdf_url_or_path.startswith('http'):
                    return pdf_processor.scrape_google_drive_pdf(pdf_url_or_path, max_chapters)
                else:
                    return pdf_processor.scrape_local_pdf(pdf_url_or_path, max_chapters)
        except Exception as e:
            self.logger.error(f"Failed to process PDF: {e}")
            return ScrapingResult(success=False, source_url=pdf_url_or_path, errors=[str(e)])
            
    def save_results(self, results: Dict[str, ScrapingResult], output_dir: str = "output") -> None:
        """Save scraping results to files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save individual source results
        for source_name, result in results.items():
            self._save_result(result, output_path / f"{source_name}.json")
            
        # Save combined results
        all_entries = []
        total_stats = {
            'total_sources': len(results),
            'successful_sources': sum(1 for r in results.values() if r.success),
            'total_entries': 0,
            'total_errors': 0,
            'scraped_at': datetime.now().isoformat()
        }
        
        for source_name, result in results.items():
            total_stats['total_entries'] += len(result.entries)
            total_stats['total_errors'] += len(result.errors)
            
            # Add source info to each entry
            for entry in result.entries:
                entry_dict = entry.dict()
                entry_dict['source_name'] = source_name
                all_entries.append(entry_dict)
                
        combined_data = {
            'metadata': total_stats,
            'entries': all_entries
        }
        
        # Save as JSON
        with open(output_path / "knowledgebase.json", 'w', encoding='utf-8') as f:
            json.dump(combined_data, f, indent=2, default=str, ensure_ascii=False)
            
        # Save as markdown for human reading
        self._save_as_markdown(all_entries, output_path / "knowledgebase.md")
        
        self.logger.info(f"Results saved to {output_path}")
        self._print_summary(total_stats)
        
    def _save_result(self, result: ScrapingResult, file_path: Path) -> None:
        """Save individual scraping result"""
        data = {
            'metadata': {
                'success': result.success,
                'source_url': result.source_url,
                'total_found': result.total_found,
                'total_scraped': result.total_scraped,
                'errors': result.errors,
                'scraped_at': datetime.now().isoformat()
            },
            'entries': [entry.dict() for entry in result.entries]
        }
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str, ensure_ascii=False)
            
    def _save_as_markdown(self, entries: List[Dict], file_path: Path) -> None:
        """Save entries as markdown file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("# Knowledgebase\n\n")
            f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            for entry in entries:
                f.write(f"## {entry['title']}\n\n")
                f.write(f"**Source:** {entry['source_domain']}\n")
                f.write(f"**URL:** {entry['url']}\n")
                f.write(f"**Type:** {entry['content_type']}\n")
                
                if entry.get('author'):
                    f.write(f"**Author:** {entry['author']['name']}\n")
                    
                if entry.get('published_date'):
                    f.write(f"**Published:** {entry['published_date']}\n")
                    
                if entry.get('tags'):
                    tags = [tag['name'] for tag in entry['tags']]
                    f.write(f"**Tags:** {', '.join(tags)}\n")
                    
                f.write("\n")
                f.write(entry['content'])
                f.write("\n\n---\n\n")
                
    def _print_summary(self, stats: Dict[str, Any]) -> None:
        """Print scraping summary"""
        print("\n" + "="*50)
        print("SCRAPING SUMMARY")
        print("="*50)
        print(f"Total sources: {stats['total_sources']}")
        print(f"Successful sources: {stats['successful_sources']}")
        print(f"Total entries: {stats['total_entries']}")
        print(f"Total errors: {stats['total_errors']}")
        print(f"Scraped at: {stats['scraped_at']}")
        print("="*50)
        
    def get_config_recommendations(self, target_sources: List[str]) -> ScrapingConfig:
        """Get recommended configuration based on target sources"""
        config = ScrapingConfig()
        
        # Adjust settings based on sources
        if any('interviewing.io' in source for source in target_sources):
            # interviewing.io might need Selenium for dynamic content
            config.delay_between_requests = 2.0  # Be more respectful
            
        if any('medium.com' in source for source in target_sources):
            # Medium can be strict about scraping
            config.delay_between_requests = 3.0
            config.max_retries = 5
            
        return config 