import time
import logging
import hashlib
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from .models import KnowledgebaseEntry, ScrapingResult, ScrapingConfig, Author, Tag


class BaseScraper(ABC):
    """Base class for all scrapers"""
    
    def __init__(self, config: ScrapingConfig = None):
        self.config = config or ScrapingConfig()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': self.config.user_agent
        })
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def __enter__(self):
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        
    def _make_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        """Make HTTP request with retries and error handling"""
        for attempt in range(self.config.max_retries):
            try:
                response = self.session.get(
                    url, 
                    timeout=self.config.timeout,
                    **kwargs
                )
                response.raise_for_status()
                return response
                
            except requests.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.config.max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                    
        self.logger.error(f"Failed to fetch {url} after {self.config.max_retries} attempts")
        return None
        
    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content"""
        return BeautifulSoup(html, 'lxml')
        
    def _extract_text_content(self, soup: BeautifulSoup, content_selector: str = None) -> str:
        """Extract main text content from HTML"""
        if content_selector:
            content_element = soup.select_one(content_selector)
            if content_element:
                soup = content_element
                
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
            
        if self.config.convert_to_markdown:
            return markdownify(str(soup), heading_style="ATX")
        else:
            return soup.get_text(strip=True, separator='\n')
            
    def _generate_id(self, url: str, title: str = "") -> str:
        """Generate unique ID for content"""
        content = f"{url}_{title}".encode('utf-8')
        return hashlib.md5(content).hexdigest()[:16]
        
    def _extract_date(self, soup: BeautifulSoup, date_selectors: List[str]) -> Optional[datetime]:
        """Try to extract publication date using multiple selectors"""
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                date_text = element.get_text(strip=True)
                # Try to parse various date formats
                try:
                    from dateutil.parser import parse
                    return parse(date_text)
                except:
                    continue
        return None
        
    def _respect_rate_limit(self):
        """Wait between requests to be respectful"""
        time.sleep(self.config.delay_between_requests)
        
    @abstractmethod
    def scrape(self, url: str) -> ScrapingResult:
        """Main scraping method - must be implemented by subclasses"""
        pass


class SeleniumScraper(BaseScraper):
    """Base scraper that uses Selenium for dynamic content"""
    
    def __init__(self, config: ScrapingConfig = None, headless: bool = True):
        super().__init__(config)
        self.headless = headless
        self.driver = None
        
    def __enter__(self):
        self._setup_driver()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.driver:
            self.driver.quit()
        super().__exit__(exc_type, exc_val, exc_tb)
        
    def _setup_driver(self):
        """Setup Chrome WebDriver"""
        chrome_options = Options()
        if self.headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument(f'--user-agent={self.config.user_agent}')
        
        try:
            self.driver = webdriver.Chrome(
                service=webdriver.chrome.service.Service(ChromeDriverManager().install()),
                options=chrome_options
            )
        except Exception as e:
            self.logger.error(f"Failed to setup WebDriver: {e}")
            raise
            
    def _wait_for_element(self, selector: str, timeout: int = 10):
        """Wait for element to be present"""
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        ) 