import re
from typing import List, Optional
from urllib.parse import urljoin, urlparse
from datetime import datetime

from .base_scraper import BaseScraper, SeleniumScraper
from .models import KnowledgebaseEntry, ScrapingResult, Author, Tag


class InterviewingIOScraper(SeleniumScraper):
    """Scraper for interviewing.io content"""
    
    def __init__(self, config=None):
        super().__init__(config)
        self.base_url = "https://interviewing.io"
        
    def scrape_blog(self, url: str = "https://interviewing.io/blog") -> ScrapingResult:
        """Scrape all blog posts from interviewing.io/blog"""
        result = ScrapingResult(success=False, source_url=url)
        
        try:
            self.driver.get(url)
            self._wait_for_element("article", timeout=15)
            
            # Find all blog post links
            blog_links = self.driver.find_elements("css selector", "a[href*='/blog/']")
            post_urls = []
            
            for link in blog_links:
                href = link.get_attribute('href')
                if href and href not in post_urls and '/blog/' in href and href != url:
                    post_urls.append(href)
                    
            result.total_found = len(post_urls)
            self.logger.info(f"Found {len(post_urls)} blog posts")
            
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
            self.logger.error(f"Failed to scrape blog index: {e}")
            result.errors.append(f"Failed to scrape blog index: {str(e)}")
            
        return result
        
    def scrape_company_guides(self, url: str = "https://interviewing.io/topics#companies") -> ScrapingResult:
        """Scrape company guides from interviewing.io/topics#companies"""
        result = ScrapingResult(success=False, source_url=url)
        
        try:
            self.driver.get(url)
            self._wait_for_element("[data-testid='company-guide']", timeout=15)
            
            # Find all company guide links
            guide_links = self.driver.find_elements("css selector", "a[href*='/topics/']")
            guide_urls = []
            
            for link in guide_links:
                href = link.get_attribute('href')
                if href and href not in guide_urls and '/topics/' in href:
                    guide_urls.append(href)
                    
            result.total_found = len(guide_urls)
            self.logger.info(f"Found {len(guide_urls)} company guides")
            
            # Scrape each guide
            for guide_url in guide_urls:
                try:
                    entry = self._scrape_guide(guide_url, "company_guide")
                    if entry:
                        result.entries.append(entry)
                        result.total_scraped += 1
                    self._respect_rate_limit()
                except Exception as e:
                    self.logger.error(f"Failed to scrape {guide_url}: {e}")
                    result.errors.append(f"Failed to scrape {guide_url}: {str(e)}")
                    
            result.success = result.total_scraped > 0
            
        except Exception as e:
            self.logger.error(f"Failed to scrape company guides: {e}")
            result.errors.append(f"Failed to scrape company guides: {str(e)}")
            
        return result
        
    def scrape_interview_guides(self, url: str = "https://interviewing.io/learn#interview-guides") -> ScrapingResult:
        """Scrape interview guides from interviewing.io/learn#interview-guides"""
        result = ScrapingResult(success=False, source_url=url)
        
        try:
            self.driver.get(url)
            self._wait_for_element("[data-testid='interview-guide']", timeout=15)
            
            # Find all interview guide links
            guide_links = self.driver.find_elements("css selector", "a[href*='/learn/']")
            guide_urls = []
            
            for link in guide_links:
                href = link.get_attribute('href')
                if href and href not in guide_urls and '/learn/' in href:
                    guide_urls.append(href)
                    
            result.total_found = len(guide_urls)
            self.logger.info(f"Found {len(guide_urls)} interview guides")
            
            # Scrape each guide
            for guide_url in guide_urls:
                try:
                    entry = self._scrape_guide(guide_url, "interview_guide")
                    if entry:
                        result.entries.append(entry)
                        result.total_scraped += 1
                    self._respect_rate_limit()
                except Exception as e:
                    self.logger.error(f"Failed to scrape {guide_url}: {e}")
                    result.errors.append(f"Failed to scrape {guide_url}: {str(e)}")
                    
            result.success = result.total_scraped > 0
            
        except Exception as e:
            self.logger.error(f"Failed to scrape interview guides: {e}")
            result.errors.append(f"Failed to scrape interview guides: {str(e)}")
            
        return result
        
    def _scrape_blog_post(self, url: str) -> Optional[KnowledgebaseEntry]:
        """Scrape individual blog post"""
        try:
            self.driver.get(url)
            self._wait_for_element("article", timeout=10)
            
            # Get page source and parse
            soup = self._parse_html(self.driver.page_source)
            
            # Extract title
            title_element = soup.select_one("h1, .post-title, .entry-title, [data-testid='post-title']")
            title = title_element.get_text(strip=True) if title_element else "Untitled"
            
            # Extract content
            content_selectors = [
                "article .content",
                ".post-content",
                ".entry-content", 
                "[data-testid='post-content']",
                "article"
            ]
            content = ""
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    content = self._extract_text_content(content_element)
                    break
                    
            if not content:
                self.logger.warning(f"No content found for {url}")
                return None
                
            # Extract author
            author = None
            author_element = soup.select_one(".author, .by-author, [data-testid='author']")
            if author_element:
                author_name = author_element.get_text(strip=True)
                author = Author(name=author_name)
                
            # Extract date
            date_selectors = [
                ".published-date",
                ".post-date", 
                "[data-testid='date']",
                "time[datetime]"
            ]
            published_date = self._extract_date(soup, date_selectors)
            
            # Extract tags
            tags = []
            tag_elements = soup.select(".tag, .category, [data-testid='tag']")
            for tag_element in tag_elements:
                tag_text = tag_element.get_text(strip=True)
                if tag_text:
                    tags.append(Tag(name=tag_text, slug=tag_text.lower().replace(' ', '-')))
                    
            return KnowledgebaseEntry(
                id=self._generate_id(url, title),
                title=title,
                url=url,
                source_domain="interviewing.io",
                content=content,
                content_type="blog_post",
                published_date=published_date,
                author=author,
                tags=tags,
                metadata={"source_section": "blog"}
            )
            
        except Exception as e:
            self.logger.error(f"Failed to scrape blog post {url}: {e}")
            return None
            
    def _scrape_guide(self, url: str, guide_type: str) -> Optional[KnowledgebaseEntry]:
        """Scrape individual guide (company or interview)"""
        try:
            self.driver.get(url)
            self._wait_for_element("main, article", timeout=10)
            
            # Get page source and parse
            soup = self._parse_html(self.driver.page_source)
            
            # Extract title
            title_element = soup.select_one("h1, .guide-title, [data-testid='guide-title']")
            title = title_element.get_text(strip=True) if title_element else "Untitled Guide"
            
            # Extract content
            content_selectors = [
                ".guide-content",
                "main .content",
                ".guide-body",
                "[data-testid='guide-content']",
                "main"
            ]
            content = ""
            for selector in content_selectors:
                content_element = soup.select_one(selector)
                if content_element:
                    content = self._extract_text_content(content_element)
                    break
                    
            if not content:
                self.logger.warning(f"No content found for {url}")
                return None
                
            # Extract company name from URL or title for company guides
            company_name = None
            if guide_type == "company_guide":
                # Try to extract company name from URL path
                path_parts = urlparse(url).path.split('/')
                if len(path_parts) > 2:
                    company_name = path_parts[-1].replace('-', ' ').title()
                    
            metadata = {
                "source_section": "company_guides" if guide_type == "company_guide" else "interview_guides"
            }
            if company_name:
                metadata["company"] = company_name
                
            return KnowledgebaseEntry(
                id=self._generate_id(url, title),
                title=title,
                url=url,
                source_domain="interviewing.io",
                content=content,
                content_type=guide_type,
                metadata=metadata
            )
            
        except Exception as e:
            self.logger.error(f"Failed to scrape guide {url}: {e}")
            return None
            
    def scrape_all(self) -> List[ScrapingResult]:
        """Scrape all content from interviewing.io"""
        results = []
        
        self.logger.info("Starting comprehensive scrape of interviewing.io")
        
        # Scrape blog posts
        blog_result = self.scrape_blog()
        results.append(blog_result)
        
        # Scrape company guides  
        company_result = self.scrape_company_guides()
        results.append(company_result)
        
        # Scrape interview guides
        interview_result = self.scrape_interview_guides()
        results.append(interview_result)
        
        return results

    def scrape(self, url: str) -> ScrapingResult:
        """Main scraping method implementation - required by BaseScraper abstract class"""
        # For interviewing.io, we default to scraping all content
        # but if a specific URL is provided, we try to determine what to scrape
        if "blog" in url:
            return self.scrape_blog(url)
        elif "topics" in url or "companies" in url:
            return self.scrape_company_guides(url)
        elif "learn" in url or "interview-guides" in url:
            return self.scrape_interview_guides(url)
        else:
            # Default to blog scraping for the main site
            return self.scrape_blog() 