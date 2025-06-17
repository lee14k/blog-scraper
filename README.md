# Blog Scraper - Knowledge Base Content Extraction

A comprehensive web scraping tool that extracts content from various sources and formats it into a standardized knowledgebase format.

## Features

🌐 **Multi-Source Scraping:**
- interviewing.io blog posts, company guides, and interview guides
- Nil Mamano's DSA blog posts
- Any generic blog (WordPress, Ghost, Jekyll, Medium, etc.)
- PDF documents (local files or Google Drive links)

📊 **Smart Content Extraction:**
- Automatic platform detection for optimal content extraction
- Markdown conversion for clean, structured content
- Metadata extraction (author, date, tags, etc.)
- PDF chapter detection and text extraction

🔧 **Configurable & Robust:**
- Rate limiting and retry mechanisms
- Selenium support for dynamic content
- Multiple output formats (JSON, Markdown)
- Comprehensive error handling and logging

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd blog-scraper
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install Chrome WebDriver (for dynamic content):**
The scraper will automatically download ChromeDriver when needed, but you can also install Chrome manually.

## Quick Start

### Scrape All Predefined Sources
```bash
python main.py --all
```

### Scrape Specific Sources
```bash
# Scrape a generic blog
python main.py --blog "https://quill.co/blog"

# Process a PDF from Google Drive
python main.py --pdf "https://drive.google.com/file/d/YOUR_FILE_ID/view"

# Process a local PDF
python main.py --pdf "path/to/document.pdf"
```

### Comprehensive Scraping
```bash
# Scrape all sources including a PDF
python main.py --all --pdf "https://drive.google.com/file/d/YOUR_FILE_ID/view"
```

## Usage Examples

### Basic Commands

```bash
# Scrape all predefined sources
python main.py --all

# Scrape a specific blog with custom delay
python main.py --blog "https://example.com/blog" --delay 2.0

# Process PDF with custom chapter limit
python main.py --pdf "document.pdf" --max-chapters 10

# Save results to custom directory
python main.py --all --output "my_results/"
```

### Advanced Configuration

```bash
# High-quality scraping with error resilience
python main.py --all \
  --delay 3.0 \
  --max-retries 5 \
  --timeout 60 \
  --output "production_data/" \
  --verbose

# Scrape multiple sources
python main.py \
  --blog "https://blog1.com" \
  --pdf "document.pdf" \
  --output "combined_results/"
```

## Output Format

The scraper produces a standardized knowledge base format:

### JSON Structure
```json
{
  "metadata": {
    "total_sources": 3,
    "successful_sources": 3,
    "total_entries": 150,
    "total_errors": 2,
    "scraped_at": "2024-01-15T10:30:00"
  },
  "entries": [
    {
      "id": "unique_identifier",
      "title": "Article Title",
      "url": "https://example.com/article",
      "source_domain": "example.com",
      "content": "# Article content in markdown format...",
      "content_type": "blog_post",
      "published_date": "2024-01-10T00:00:00",
      "author": {
        "name": "Author Name",
        "email": "author@example.com"
      },
      "tags": [
        {"name": "Technology", "slug": "technology"},
        {"name": "Programming", "slug": "programming"}
      ],
      "scraped_at": "2024-01-15T10:30:00",
      "metadata": {
        "source_section": "blog",
        "detected_platform": "wordpress"
      }
    }
  ]
}
```

### Output Files
- `knowledgebase.json` - Complete dataset in JSON format
- `knowledgebase.md` - Human-readable markdown version
- `{source_name}.json` - Individual source results
- Individual source files for debugging

## Supported Sources

### 🎯 Predefined Sources
1. **interviewing.io**
   - Blog posts (`/blog`)
   - Company guides (`/topics#companies`)
   - Interview guides (`/learn#interview-guides`)

2. **nilmamano.com**
   - DSA category blog posts (`/blog/category/dsa`)

### 🌐 Generic Blog Support
The scraper can automatically detect and extract content from:
- WordPress sites
- Ghost blogs
- Jekyll sites
- Medium articles
- Custom blog platforms

### 📄 PDF Processing
- Local PDF files
- Google Drive shared PDFs
- Automatic chapter detection
- Text extraction and cleaning

## Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `--delay` | Delay between requests (seconds) | 1.0 |
| `--max-retries` | Maximum request retries | 3 |
| `--timeout` | Request timeout (seconds) | 30 |
| `--max-chapters` | Max PDF chapters to extract | 8 |
| `--output` | Output directory | "output" |
| `--format` | Output format (json/markdown/both) | "both" |
| `--verbose` | Enable verbose logging | False |

## Architecture

```
src/
├── models.py              # Data models and schemas
├── base_scraper.py        # Base scraper classes
├── interviewing_io_scraper.py  # interviewing.io specific scraper
├── nilmamano_scraper.py   # Nil Mamano's blog scraper
├── generic_blog_scraper.py     # Universal blog scraper
├── pdf_processor.py       # PDF processing module
└── scraper_manager.py     # Main orchestration logic
```

### Key Components

1. **Base Scraper**: Common functionality for HTTP requests, rate limiting, and content extraction
2. **Specialized Scrapers**: Platform-specific logic for optimal content extraction
3. **Generic Scraper**: Universal blog scraper with platform auto-detection
4. **PDF Processor**: Handle local and Google Drive PDFs with chapter detection
5. **Scraper Manager**: Orchestrates all scrapers and manages output

## Troubleshooting

### Common Issues

**Chrome/ChromeDriver Issues:**
```bash
# Update ChromeDriver
pip install --upgrade webdriver-manager
```

**Rate Limiting:**
```bash
# Increase delay between requests
python main.py --all --delay 3.0
```

**Large PDFs:**
```bash
# Limit chapter extraction
python main.py --pdf "large.pdf" --max-chapters 5
```

**Google Drive Access:**
- Ensure the PDF link is publicly accessible
- Use the share link format: `https://drive.google.com/file/d/FILE_ID/view`

### Debug Mode
```bash
python main.py --all --verbose
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Roadmap

- [ ] Support for more blog platforms
- [ ] Database storage options
- [ ] Web interface
- [ ] Scheduled scraping
- [ ] Content deduplication
- [ ] Full-text search integration
