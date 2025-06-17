#!/usr/bin/env python3
"""
Example script showing how to use the blog scraper programmatically
"""

import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.scraper_manager import ScraperManager
from src.models import ScrapingConfig


def example_basic_usage():
    """Example: Basic scraping of all sources"""
    print("=== Basic Usage Example ===")
    
    # Create configuration
    config = ScrapingConfig(
        delay_between_requests=1.5,  # Be respectful
        max_retries=3,
        timeout=30
    )
    
    # Create manager
    manager = ScraperManager(config)
    
    # Scrape all predefined sources
    results = manager.scrape_all_sources()
    
    # Save results
    manager.save_results(results, "example_output")
    
    print("Basic scraping completed!")


def example_generic_blog():
    """Example: Scraping a generic blog"""
    print("=== Generic Blog Example ===")
    
    manager = ScraperManager()
    
    # Scrape a generic blog (replace with actual blog URL)
    blog_url = "https://quill.co/blog"  # Example blog
    result = manager.scrape_generic_blog(blog_url)
    
    print(f"Found {len(result.entries)} blog posts from {blog_url}")
    
    # Save individual result
    manager.save_results({'quill_blog': result}, "blog_output")


def example_pdf_processing():
    """Example: Processing a PDF"""
    print("=== PDF Processing Example ===")
    
    manager = ScraperManager()
    
    # Process a Google Drive PDF (replace with actual URL)
    # pdf_url = "https://drive.google.com/file/d/YOUR_FILE_ID/view"
    
    # For this example, let's use a local PDF if it exists
    local_pdf = "example.pdf"
    if Path(local_pdf).exists():
        result = manager.scrape_pdf(local_pdf, max_chapters=5)
        print(f"Extracted {len(result.entries)} chapters from PDF")
        manager.save_results({'example_pdf': result}, "pdf_output")
    else:
        print(f"Local PDF {local_pdf} not found. Skipping PDF example.")


def example_custom_sources():
    """Example: Scraping specific custom sources"""
    print("=== Custom Sources Example ===")
    
    # Custom configuration for specific needs
    config = ScrapingConfig(
        delay_between_requests=2.0,  # Slower for respectful scraping
        max_retries=5,
        timeout=60,
        convert_to_markdown=True
    )
    
    manager = ScraperManager(config)
    
    # List of blogs to scrape
    blogs_to_scrape = [
        "https://example1.com/blog",
        "https://example2.com/articles",
        # Add more blog URLs here
    ]
    
    results = {}
    for i, blog_url in enumerate(blogs_to_scrape):
        try:
            print(f"Scraping blog {i+1}: {blog_url}")
            result = manager.scrape_generic_blog(blog_url)
            results[f'custom_blog_{i+1}'] = result
        except Exception as e:
            print(f"Failed to scrape {blog_url}: {e}")
    
    if results:
        manager.save_results(results, "custom_output")


def example_comprehensive():
    """Example: Comprehensive scraping with all features"""
    print("=== Comprehensive Example ===")
    
    # Create optimized configuration
    config = ScrapingConfig(
        delay_between_requests=1.5,
        max_retries=3,
        timeout=45,
        max_content_length=200000,  # Larger content limit
        convert_to_markdown=True,
        save_raw_html=False  # Save space
    )
    
    manager = ScraperManager(config)
    
    # Scrape everything
    print("Starting comprehensive scrape...")
    
    # 1. All predefined sources
    all_results = manager.scrape_all_sources()
    
    # 2. Additional custom blogs
    custom_blogs = [
        # Add your favorite blogs here
        # "https://your-favorite-blog.com",
    ]
    
    for i, blog_url in enumerate(custom_blogs):
        try:
            result = manager.scrape_generic_blog(blog_url)
            all_results[f'additional_blog_{i+1}'] = result
        except Exception as e:
            print(f"Failed to scrape {blog_url}: {e}")
    
    # 3. Save comprehensive results
    manager.save_results(all_results, "comprehensive_output")
    
    print("Comprehensive scraping completed!")


if __name__ == "__main__":
    print("Blog Scraper Examples")
    print("=" * 50)
    
    # Run examples
    try:
        example_basic_usage()
        print()
        
        example_generic_blog()
        print()
        
        example_pdf_processing()
        print()
        
        # Uncomment to run more examples
        # example_custom_sources()
        # example_comprehensive()
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc() 