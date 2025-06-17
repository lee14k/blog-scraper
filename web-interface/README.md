# Blog Scraper Web Interface

A modern Next.js web interface for the blog scraper tool with real-time progress tracking and results visualization.

## Features

- **Multi-Source Scraping**: Support for various blog sources including:
  - interviewing.io (blog posts, company guides, interview guides)
  - nilmamano.com (Data Structures & Algorithms posts)
  - Generic blog scraping for any blog URL
  - PDF processing (local files or Google Drive URLs)
  - All sources at once with combined results

- **Real-Time Monitoring**: 
  - Live progress updates during scraping
  - Real-time job status tracking
  - Detailed logging for each operation

- **Results Management**:
  - Interactive results viewer
  - Detailed metadata display
  - Content preview and search
  - Export capabilities

- **Modern UI**:
  - Responsive design with Tailwind CSS
  - Toast notifications for user feedback
  - Progress bars and status indicators
  - Clean, intuitive interface

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- pip

### Starting the Application

You need to run both the FastAPI backend and Next.js frontend:

#### 1. Start the FastAPI Backend

From the project root directory:

```bash
cd web-interface
python run_api.py
```

This will start the FastAPI server on http://localhost:8000

#### 2. Start the Next.js Frontend

In a new terminal, from the web-interface directory:

```bash
npm install
npm run dev
```

This will start the Next.js development server on http://localhost:3000

### Environment Configuration

The frontend expects the FastAPI backend to be running on `http://localhost:8000` by default. If you need to change this, update the `FASTAPI_BASE_URL` in the API route.

## Usage

1. **Navigate to http://localhost:3000** in your browser
2. **Choose a scraping operation** from the dashboard:
   - Click any of the colored buttons to start scraping
   - Configure settings using the gear icon
   - Monitor progress in real-time
3. **View results** in the results panel on the right
4. **Export or download** processed content as needed

## API Endpoints

The frontend connects to these FastAPI endpoints:

- `POST /scrape/all` - Scrape all sources
- `POST /scrape/interviewing-io/all` - Scrape all interviewing.io content  
- `POST /scrape/nilmamano` - Scrape nilmamano.com DSA posts
- `POST /scrape/generic-blog` - Scrape any blog URL
- `POST /scrape/pdf` - Process PDF documents

## Development

### Frontend Development

```bash
cd web-interface
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
```

### Backend Development

The FastAPI backend is located in the main project directory. See the main README for backend development instructions.

## Troubleshooting

### Common Issues

1. **API Connection Failed**
   - Ensure the FastAPI backend is running on port 8000
   - Check console for CORS errors
   - Verify firewall settings

2. **Import Errors in FastAPI**
   - Make sure you're running `python run_api.py` from the `web-interface` directory
   - Check that all dependencies are installed: `pip install -r requirements.txt`

3. **Frontend Build Errors**
   - Clear node_modules and reinstall: `rm -rf node_modules && npm install`
   - Check Node.js version compatibility

### Development Tips

- Use browser dev tools to monitor API requests
- Check FastAPI logs for backend issues
- Toast notifications will show success/error messages
- Progress bars indicate real-time scraping status

## Architecture

```
Frontend (Next.js) → API Route (/api/scrape) → FastAPI Backend → Scrapers
```

The Next.js API route acts as a proxy, handling:
- Request transformation between frontend and backend formats
- Streaming progress updates
- Error handling and user feedback
- CORS and authentication (if needed)

## Contributing

1. Follow the existing code style
2. Add TypeScript types for new features
3. Test both frontend and backend integration
4. Update documentation for new endpoints or features 