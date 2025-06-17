import re
from typing import List, Optional
from urllib.parse import urljoin, urlparse
from datetime import datetime

from .base_scraper import BaseScraper
from .models import KnowledgebaseEntry, ScrapingResult, Author, Tag


class NilMamanoScraper(BaseScraper):
    """Scraper for Nil Mamano's DS&A blog posts"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.base_url = "https://nilmamano.com"
        
    def scrape_dsa_posts(self, url: str = "https://nilmamano.com/blog/category/dsa") -> ScrapingResult:
        """Scrape all DS&A blog posts from nilmamano.com"""
        result = ScrapingResult(success=False, source_url=url)
        
        try:
            response = self._make_request(url)
            if not response:
                result.errors.append(f"Failed to fetch {url}")
                return result
                
            soup = self._parse_html(response.text)
            
            # Find all blog post links
            post_links = soup.select("a[href*='/blog/']")
            post_urls = []
            
            for link in post_links:
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = urljoin(self.base_url, href)
                    
                    # Filter to only DSA posts and avoid duplicates
                    if href not in post_urls and '/blog/' in href and href != url:
                        post_urls.append(href)
                        
            # Also check for pagination
            pagination_links = soup.select(".pagination a, .page-numbers a")
            for link in pagination_links:
                href = link.get('href')
                if href and 'page' in href:
                    page_url = urljoin(url, href)
                    # Recursively scrape paginated pages
                    page_result = self.scrape_dsa_posts(page_url)
                    for entry in page_result.entries:
                        if entry.url not in [e.url for e in result.entries]:
                            result.entries.append(entry)
                            
            result.total_found = len(post_urls)
            self.logger.info(f"Found {len(post_urls)} DSA blog posts")
            
            # Scrape each blog post
            for post_url in post_urls:
                try:
                    entry = self._scrape_blog_post(post_url)
                    if entry:
                        result.entries.append(entry)
                        result.total_scraped += 1
                    self._respect_rate_limit()
                except Exception as e:
                    self.logger.error(f"Failed to scrape {post_url}: {e}")
                    result.errors.append(f"Failed to scrape {post_url}: {str(e)}")
                    
            result.success = result.total_scraped > 0
            
        except Exception as e:
            self.logger.error(f"Failed to scrape DSA blog index: {e}")
            result.errors.append(f"Failed to scrape DSA blog index: {str(e)}")
            
        return result
        
    def _scrape_blog_post(self, url: str) -> Optional[KnowledgebaseEntry]:
        """Scrape individual blog post"""
        try:
            response = self._make_request(url)
            if not response:
                return None
                
            soup = self._parse_html(response.text)
            
            # Extract title
            title_element = soup.select_one("h1, .post-title, .entry-title, .article-title")
            title = title_element.get_text(strip=True) if title_element else "Untitled"
            
            # Extract content - try multiple selectors
            content_selectors = [
                ".post-content",
                ".entry-content", 
                ".article-content",
                ".content",
                "article .post-body",
                "main article"
            ]
            content = ""
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    content = self._extract_text_content(content_element)
                    break
                    
            if not content:
                # Fallback: try to get content from the main article tag
                article = soup.select_one("article")
                if article:
                    content = self._extract_text_content(article)
                    
            if not content:
                self.logger.warning(f"No content found for {url}")
                return None
                
            # Extract excerpt/summary
            excerpt = None
            excerpt_element = soup.select_one(".excerpt, .summary, .post-excerpt")
            if excerpt_element:
                excerpt = excerpt_element.get_text(strip=True)[:500]
                
            # Extract author (should be Nil Mamano)
            author = Author(name="Nil Mamano", url="https://nilmamano.com")
            
            # Extract date
            date_selectors = [
                ".post-date",
                ".published-date",
                ".entry-date",
                "time[datetime]",
                ".date"
            ]
            published_date = self._extract_date(soup, date_selectors)
            
            # Extract tags/categories
            tags = [Tag(name="DSA", slug="dsa"), Tag(name="Data Structures", slug="data-structures")]
            tag_elements = soup.select(".tag, .category, .post-tag")
            for tag_element in tag_elements:
                tag_text = tag_element.get_text(strip=True)
                if tag_text and tag_text not in [t.name for t in tags]:
                    tags.append(Tag(name=tag_text, slug=tag_text.lower().replace(' ', '-')))
                    
            # Check if this is actually a DSA post by looking for keywords
            dsa_keywords = ['algorithm', 'data structure', 'complexity', 'big o', 'leetcode', 
                           'binary search', 'dynamic programming', 'graph', 'tree', 'array', 
                           'linked list', 'stack', 'queue', 'hash', 'sorting']
            
            content_lower = content.lower()
            title_lower = title.lower()
            is_dsa_post = any(keyword in content_lower or keyword in title_lower for keyword in dsa_keywords)
            
            if not is_dsa_post:
                self.logger.info(f"Skipping non-DSA post: {title}")
                return None
                
            return KnowledgebaseEntry(
                id=self._generate_id(url, title),
                title=title,
                url=url,
                source_domain="nilmamano.com",
                content=content,
                excerpt=excerpt,
                content_type="blog_post",
                published_date=published_date,
                author=author,
                tags=tags,
                metadata={
                    "category": "DSA",
                    "author_website": "https://nilmamano.com"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to scrape blog post {url}: {e}")
            return None
            
    def scrape(self, url: str) -> ScrapingResult:
        """Main scrape method"""
        return self.scrape_dsa_posts(url) 