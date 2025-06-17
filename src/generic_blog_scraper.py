import re
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse, urlencode
from datetime import datetime

from .base_scraper import BaseScraper, SeleniumScraper
from .models import KnowledgebaseEntry, ScrapingResult, Author, Tag


class GenericBlogScraper(BaseScraper):
    """Generic scraper that can work with most blog sites"""
    
    def __init__(self, config=None):
        super().__init__(config)
        
    def scrape_blog(self, blog_url: str, max_pages: int = 10) -> ScrapingResult:
        """Scrape all posts from a generic blog"""
        result = ScrapingResult(success=False, source_url=blog_url)
        
        try:
            parsed_url = urlparse(blog_url)
            base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
            
            # First, try to find the blog index or main page
            blog_index_url = self._find_blog_index(blog_url)
            
            response = self._make_request(blog_index_url)
            if not response:
                result.errors.append(f"Failed to fetch {blog_index_url}")
                return result
                
            soup = self._parse_html(response.text)
            
            # Detect the blog platform/structure
            platform_info = self._detect_blog_platform(soup)
            self.logger.info(f"Detected platform: {platform_info}")
            
            # Find all blog post links
            post_urls = self._extract_post_urls(soup, base_domain, platform_info)
            
            # Handle pagination
            page_count = 1
            while page_count < max_pages:
                next_page_url = self._find_next_page(soup, blog_index_url, page_count)
                if not next_page_url:
                    break
                    
                self._respect_rate_limit()
                page_response = self._make_request(next_page_url)
                if page_response:
                    page_soup = self._parse_html(page_response.text)
                    page_post_urls = self._extract_post_urls(page_soup, base_domain, platform_info)
                    post_urls.extend([url for url in page_post_urls if url not in post_urls])
                    soup = page_soup  # Update for next iteration
                    
                page_count += 1
                
            result.total_found = len(post_urls)
            self.logger.info(f"Found {len(post_urls)} blog posts")
            
            # Scrape each blog post
            for post_url in post_urls:
                try:
                    entry = self._scrape_blog_post(post_url, platform_info)
                    if entry:
                        result.entries.append(entry)
                        result.total_scraped += 1
                    self._respect_rate_limit()
                except Exception as e:
                    self.logger.error(f"Failed to scrape {post_url}: {e}")
                    result.errors.append(f"Failed to scrape {post_url}: {str(e)}")
                    
            result.success = result.total_scraped > 0
            
        except Exception as e:
            self.logger.error(f"Failed to scrape blog: {e}")
            result.errors.append(f"Failed to scrape blog: {str(e)}")
            
        return result
        
    def _find_blog_index(self, url: str) -> str:
        """Try to find the main blog index page"""
        # Common blog paths
        blog_paths = ['/blog', '/posts', '/articles', '/news', '/insights']
        
        parsed_url = urlparse(url)
        base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
        
        # If URL already contains blog path, use it
        for path in blog_paths:
            if path in parsed_url.path:
                return url
                
        # If it's just the domain, try adding blog paths
        if parsed_url.path in ['', '/']:
            for path in blog_paths:
                test_url = urljoin(base_url, path)
                response = self._make_request(test_url)
                if response and response.status_code == 200:
                    return test_url
                    
        return url
        
    def _detect_blog_platform(self, soup) -> Dict[str, Any]:
        """Detect the blog platform and common selectors"""
        platform_info = {
            'platform': 'unknown',
            'post_selectors': [],
            'title_selectors': [],
            'content_selectors': [],
            'date_selectors': [],
            'author_selectors': []
        }
        
        # Check for common platforms
        if soup.select('.wp-block-post') or soup.select('.post-content'):
            platform_info['platform'] = 'wordpress'
            platform_info['post_selectors'] = ['article.post', '.post', '.wp-block-post']
            platform_info['title_selectors'] = ['h1.entry-title', 'h2.entry-title', '.post-title h1', '.post-title h2']
            platform_info['content_selectors'] = ['.entry-content', '.post-content', '.wp-block-post-content']
            platform_info['date_selectors'] = ['.published', '.post-date', '.entry-date', 'time']
            platform_info['author_selectors'] = ['.author', '.byline', '.post-author']
            
        elif soup.select('.medium-post') or 'medium.com' in str(soup):
            platform_info['platform'] = 'medium'
            platform_info['post_selectors'] = ['article', '.medium-post']
            platform_info['title_selectors'] = ['h1', '.graf--title']
            platform_info['content_selectors'] = ['.postArticle-content', '.section-content']
            
        elif soup.select('.ghost-post') or soup.select('.post-card'):
            platform_info['platform'] = 'ghost'
            platform_info['post_selectors'] = ['article.post', '.post-card']
            platform_info['title_selectors'] = ['h1.post-title', '.post-card-title']
            platform_info['content_selectors'] = ['.post-content', '.gh-content']
            
        elif soup.select('.jekyll-post') or soup.select('.post-content'):
            platform_info['platform'] = 'jekyll'
            platform_info['post_selectors'] = ['article.post', '.post']
            platform_info['title_selectors'] = ['h1.post-title', '.post-header h1']
            platform_info['content_selectors'] = ['.post-content', '.post-body']
            
        else:
            # Generic fallback selectors
            platform_info['post_selectors'] = ['article', '.post', '.blog-post', '.entry']
            platform_info['title_selectors'] = ['h1', 'h2', '.title', '.post-title', '.entry-title']
            platform_info['content_selectors'] = ['.content', '.post-content', '.entry-content', '.article-content']
            platform_info['date_selectors'] = ['.date', '.published', '.post-date', 'time']
            platform_info['author_selectors'] = ['.author', '.byline', '.post-author']
            
        return platform_info
        
    def _extract_post_urls(self, soup, base_domain: str, platform_info: Dict) -> List[str]:
        """Extract blog post URLs from the page"""
        post_urls = []
        
        # Common link patterns for blog posts
        link_patterns = [
            'a[href*="/blog/"]',
            'a[href*="/post/"]', 
            'a[href*="/posts/"]',
            'a[href*="/article/"]',
            'a[href*="/articles/"]'
        ]
        
        # Platform-specific selectors
        if platform_info['platform'] == 'wordpress':
            link_patterns.extend(['a[rel="bookmark"]', '.post-title a', '.entry-title a'])
        elif platform_info['platform'] == 'medium':
            link_patterns.extend(['a[data-action="open-post"]', '.medium-post a'])
        elif platform_info['platform'] == 'ghost':
            link_patterns.extend(['.post-card-title a', '.post-title a'])
            
        # Try each pattern
        for pattern in link_patterns:
            links = soup.select(pattern)
            for link in links:
                href = link.get('href')
                if href:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        href = urljoin(base_domain, href)
                    elif not href.startswith('http'):
                        continue
                        
                    # Filter out non-post URLs
                    if self._is_likely_blog_post(href) and href not in post_urls:
                        post_urls.append(href)
                        
        # Fallback: look for any links in post containers
        for selector in platform_info['post_selectors']:
            post_containers = soup.select(selector)
            for container in post_containers:
                links = container.select('a[href]')
                for link in links:
                    href = link.get('href')
                    if href:
                        if href.startswith('/'):
                            href = urljoin(base_domain, href)
                        if self._is_likely_blog_post(href) and href not in post_urls:
                            post_urls.append(href)
                            
        return post_urls
        
    def _is_likely_blog_post(self, url: str) -> bool:
        """Check if URL is likely a blog post"""
        url_lower = url.lower()
        
        # Exclude common non-post pages
        exclude_patterns = [
            '/tag/', '/category/', '/author/', '/page/', '/feed', '/rss',
            '/about', '/contact', '/privacy', '/terms', '/archive',
            '.xml', '.rss', '.json', '.css', '.js', '.jpg', '.png', '.gif'
        ]
        
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False
                
        # Include patterns that suggest blog posts
        include_patterns = [
            '/blog/', '/post/', '/posts/', '/article/', '/articles/',
            '/news/', '/insights/', '/tutorial/', '/guide/'
        ]
        
        return any(pattern in url_lower for pattern in include_patterns)
        
    def _find_next_page(self, soup, current_url: str, page_num: int) -> Optional[str]:
        """Find next page URL for pagination"""
        # Common pagination selectors
        next_selectors = [
            '.next', '.next-page', '.pagination .next', 
            'a[rel="next"]', '.wp-pagenavi .next',
            '.pagination-next', '.nav-next a'
        ]
        
        for selector in next_selectors:
            next_link = soup.select_one(selector)
            if next_link and next_link.get('href'):
                href = next_link.get('href')
                if href.startswith('/'):
                    return urljoin(current_url, href)
                return href
                
        # Try numbered pagination
        page_links = soup.select('.pagination a, .page-numbers a')
        for link in page_links:
            text = link.get_text(strip=True)
            if text.isdigit() and int(text) == page_num + 1:
                href = link.get('href')
                if href.startswith('/'):
                    return urljoin(current_url, href)
                return href
                
        return None
        
    def _scrape_blog_post(self, url: str, platform_info: Dict) -> Optional[KnowledgebaseEntry]:
        """Scrape individual blog post"""
        try:
            response = self._make_request(url)
            if not response:
                return None
                
            soup = self._parse_html(response.text)
            domain = urlparse(url).netloc
            
            # Extract title
            title = "Untitled"
            for selector in platform_info['title_selectors']:
                title_element = soup.select_one(selector)
                if title_element:
                    title = title_element.get_text(strip=True)
                    break
                    
            if title == "Untitled":
                # Fallback title extraction
                title_element = soup.select_one('h1, title, .title')
                if title_element:
                    title = title_element.get_text(strip=True)
                    
            # Extract content
            content = ""
            for selector in platform_info['content_selectors']:
                content_element = soup.select_one(selector)
                if content_element:
                    content = self._extract_text_content(content_element)
                    break
                    
            if not content:
                # Fallback content extraction
                main_content = soup.select_one('main, article, .main-content')
                if main_content:
                    content = self._extract_text_content(main_content)
                    
            if not content:
                self.logger.warning(f"No content found for {url}")
                return None
                
            # Extract author
            author = None
            for selector in platform_info['author_selectors']:
                author_element = soup.select_one(selector)
                if author_element:
                    author_name = author_element.get_text(strip=True)
                    author = Author(name=author_name)
                    break
                    
            # Extract date
            published_date = self._extract_date(soup, platform_info['date_selectors'])
            
            # Extract tags
            tags = []
            tag_elements = soup.select('.tag, .tags a, .category, .categories a')
            for tag_element in tag_elements:
                tag_text = tag_element.get_text(strip=True)
                if tag_text:
                    tags.append(Tag(name=tag_text, slug=tag_text.lower().replace(' ', '-')))
                    
            return KnowledgebaseEntry(
                id=self._generate_id(url, title),
                title=title,
                url=url,
                source_domain=domain,
                content=content,
                content_type="blog_post",
                published_date=published_date,
                author=author,
                tags=tags,
                metadata={
                    "detected_platform": platform_info['platform']
                }
            )
            
        except Exception as e:
            self.logger.error(f"Failed to scrape blog post {url}: {e}")
            return None
            
    def scrape(self, url: str) -> ScrapingResult:
        """Main scrape method"""
        return self.scrape_blog(url) 