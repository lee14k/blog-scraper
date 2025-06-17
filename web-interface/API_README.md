# Blog Scraper FastAPI Service

This FastAPI service converts the existing Python scrapers into REST API endpoints.

## Setup

1. Install dependencies:
```bash
cd web-interface
pip install -r requirements.txt
```

2. Run the API server:
```bash
python run_api.py
```

The API will be available at `http://localhost:8000`

## Available Endpoints

### Root Endpoint
- `GET /` - API information and available endpoints

### Scraping Endpoints

1. **Nilmamano DSA Posts**
   - `POST /scrape/nilmamano`
   - Scrapes DS&A posts from nilmamano.com
   
2. **Interviewing.io Content**
   - `POST /scrape/interviewing-io/blog` - Blog posts
   - `POST /scrape/interviewing-io/company-guides` - Company guides
   - `POST /scrape/interviewing-io/interview-guides` - Interview guides
   - `POST /scrape/interviewing-io/all` - All content

3. **Generic Blog**
   - `POST /scrape/generic-blog` - Scrape any blog

4. **PDF Processing**
   - `POST /scrape/pdf` - Process PDF from URL or path

5. **All Sources**
   - `POST /scrape/all` - Scrape all predefined sources
   - `POST /scrape/all/background` - Start scraping in background

### Health Check
- `GET /health` - Service health status

## Request Examples

### Scrape Nilmamano
```bash
curl -X POST "http://localhost:8000/scrape/nilmamano" \
     -H "Content-Type: application/json" \
     -d '{}'
```

### Scrape Generic Blog
```bash
curl -X POST "http://localhost:8000/scrape/generic-blog" \
     -H "Content-Type: application/json" \
     -d '{"blog_url": "https://example-blog.com"}'
```

### Custom Configuration
```bash
curl -X POST "http://localhost:8000/scrape/nilmamano" \
     -H "Content-Type: application/json" \
     -d '{
       "config": {
         "delay_between_requests": 2.0,
         "max_retries": 5,
         "convert_to_markdown": true
       }
     }'
```

## API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Response Format

All scraping endpoints return a `ScrapingResult` object:

```json
{
  "success": true,
  "entries": [
    {
      "id": "unique-id",
      "title": "Article Title",
      "url": "https://example.com/article",
      "source_domain": "example.com",
      "content": "Article content in markdown...",
      "content_type": "blog_post",
      "published_date": "2023-01-01T00:00:00",
      "author": {
        "name": "Author Name"
      },
      "tags": [
        {"name": "Tag Name", "slug": "tag-name"}
      ]
    }
  ],
  "errors": [],
  "total_found": 10,
  "total_scraped": 8,
  "source_url": "https://example.com"
}
```

## Error Handling

The API includes comprehensive error handling:
- Invalid URLs return 422 status
- Scraping failures return 500 status with error details
- All errors are logged for debugging

## Background Tasks

For long-running operations, use the background endpoints:
- Results are saved automatically to the `output` directory
- Check logs for completion status 