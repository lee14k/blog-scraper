#!/usr/bin/env python3
"""
Blog Scraper - Extract content into knowledgebase format

This tool can scrape content from:
- interviewing.io blog posts, company guides, and interview guides
- Nil Mamano's DSA blog posts
- Any generic blog
- PDF documents (including from Google Drive)
"""

import argparse
import sys
from pathlib import Path

# Add src to path so we can import our modules
sys.path.append(str(Path(__file__).parent / "src"))

from src.scraper_manager import ScraperManager
from src.models import ScrapingConfig


def main():
    parser = argparse.ArgumentParser(
        description="Scrape content into knowledgebase format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape all predefined sources
  python main.py --all
  
  # Scrape all predefined sources including PDF
  python main.py --all --pdf "https://drive.google.com/file/d/YOUR_FILE_ID/view"
  
  # Scrape a specific blog
  python main.py --blog "https://quill.co/blog"
  
  # Process a PDF
  python main.py --pdf "path/to/book.pdf" --max-chapters 10
  
  # Scrape with custom settings
  python main.py --all --delay 2.0 --output results/
        """
    )
    
    # Source selection
    parser.add_argument(
        '--all', 
        action='store_true',
        help='Scrape all predefined sources (interviewing.io, nilmamano.com)'
    )
    parser.add_argument(
        '--blog', 
        type=str,
        help='Scrape a specific blog URL'
    )
    parser.add_argument(
        '--pdf', 
        type=str,
        help='Process a PDF file (local path or Google Drive URL)'
    )
    
    # Configuration options
    parser.add_argument(
        '--delay', 
        type=float, 
        default=1.0,
        help='Delay between requests in seconds (default: 1.0)'
    )
    parser.add_argument(
        '--max-retries', 
        type=int, 
        default=3,
        help='Maximum number of retries for failed requests (default: 3)'
    )
    parser.add_argument(
        '--timeout', 
        type=int, 
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    parser.add_argument(
        '--max-chapters', 
        type=int, 
        default=8,
        help='Maximum number of chapters to extract from PDFs (default: 8)'
    )
    
    # Output options
    parser.add_argument(
        '--output', 
        type=str, 
        default='output',
        help='Output directory (default: output)'
    )
    parser.add_argument(
        '--format', 
        choices=['json', 'markdown', 'both'], 
        default='both',
        help='Output format (default: both)'
    )
    
    # Other options
    parser.add_argument(
        '--verbose', 
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--headless', 
        action='store_true', 
        default=True,
        help='Run browser in headless mode (default: True)'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not any([args.all, args.blog, args.pdf]):
        parser.error("Must specify at least one of: --all, --blog, or --pdf")
    
    # Create configuration
    config = ScrapingConfig(
        delay_between_requests=args.delay,
        max_retries=args.max_retries,
        timeout=args.timeout,
        output_format=args.format
    )
    
    # Create scraper manager
    manager = ScraperManager(config)
    
    try:
        results = {}
        
        if args.all:
            print("🚀 Starting comprehensive scrape of all sources...")
            results.update(manager.scrape_all_sources(args.pdf))
            
        if args.blog:
            print(f"🌐 Scraping blog: {args.blog}")
            results['custom_blog'] = manager.scrape_generic_blog(args.blog)
            
        if args.pdf and not args.all:
            print(f"📄 Processing PDF: {args.pdf}")
            results['pdf'] = manager.scrape_pdf(args.pdf, args.max_chapters)
            
        # Save results
        if results:
            print("💾 Saving results...")
            manager.save_results(results, args.output)
            print("✅ Scraping completed successfully!")
        else:
            print("❌ No results to save")
            
    except KeyboardInterrupt:
        print("\n⏹️  Scraping interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error during scraping: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main() 