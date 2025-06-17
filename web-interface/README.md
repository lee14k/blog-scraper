# Blog Scraper Web Interface

A beautiful Next.js frontend for the blog scraper tool with real-time progress tracking and results visualization.

## Features

🎨 **Modern UI**: Clean, responsive interface built with Tailwind CSS
🚀 **Real-time Progress**: Live updates during scraping operations  
📊 **Results Dashboard**: Browse and download scraping results
⚙️ **Configurable**: Adjust scraping parameters through the UI
📱 **Responsive**: Works on desktop, tablet, and mobile

## Screenshots

- **Dashboard**: Overview with stats and quick action buttons
- **Progress Tracking**: Real-time job monitoring with logs
- **Results Viewer**: Browse entries and download data
- **Configuration**: Adjust delays, retries, and other settings

## Setup Instructions

### 1. Install Dependencies

```bash
cd web-interface
npm install
```

### 2. Configure the Project

The frontend is configured to work with the Python scraper in the parent directory. Make sure your folder structure looks like this:

```
blog-scraper/
├── src/                    # Python scraper source
├── main.py                 # Python CLI
├── requirements.txt        # Python dependencies
└── web-interface/         # Next.js frontend
    ├── src/
    ├── package.json
    └── ...
```

### 3. Start the Development Server

```bash
npm run dev
```

The interface will be available at `http://localhost:3000`

## Usage

### Dashboard Overview

The main dashboard provides:

- **Active Jobs Counter**: Shows currently running scraping operations
- **Completed Jobs**: Historical results count
- **Total Entries**: Sum of all scraped entries

### Scraping Operations

Click any button to start scraping:

1. **🚀 Scrape All Sources**: Complete scrape of all predefined sources
2. **📄 interviewing.io**: Blog posts, company guides, interview guides  
3. **🟣 Nil Mamano DSA**: Data structures & algorithms posts
4. **🌐 Generic Blog**: Enter any blog URL to scrape
5. **📄 PDF Document**: Local files or Google Drive links

### Configuration

Click the **Configure** button to adjust:

- **Delay Between Requests**: Respectful rate limiting (default: 1.0s)
- **Max Retries**: Retry failed requests (default: 3)
- **Timeout**: Request timeout in seconds (default: 30)
- **Max PDF Chapters**: Limit PDF extraction (default: 8)
- **Output Directory**: Where to save results (default: 'output')

### Progress Tracking

Active jobs show:

- **Real-time progress bar** with percentage
- **Live logs** from the Python scraper
- **Status indicators**: Pending ⏳, Running 🚀, Complete ✅, Failed ❌
- **Expandable log viewer** for debugging

### Results Viewer

Browse completed jobs:

- **Summary statistics** (found, scraped, errors)
- **Sample entries** with titles, content previews, and tags
- **Download button** to export results as JSON
- **Clickable entries** to view full details

## API Integration

The frontend communicates with the Python scraper through:

### `/api/scrape` (POST)

Starts a scraping job with streaming progress updates.

**Request Body:**
```json
{
  "type": "all" | "interviewing-io" | "nilmamano" | "generic-blog" | "pdf",
  "config": {
    "delay": 1.0,
    "maxRetries": 3,
    "timeout": 30,
    "maxChapters": 8,
    "blogUrl": "https://example.com/blog",
    "pdfUrl": "path/to/file.pdf",
    "outputDir": "output"
  },
  "jobId": "unique-job-id"
}
```

**Response:** Streaming JSON lines with progress updates and final results.

## Development

### Project Structure

```
web-interface/
├── src/
│   ├── app/
│   │   ├── layout.tsx         # Root layout
│   │   ├── page.tsx          # Main dashboard
│   │   ├── globals.css       # Global styles
│   │   └── api/
│   │       └── scrape/
│   │           └── route.ts  # API endpoint
│   ├── components/
│   │   ├── ScrapingDashboard.tsx  # Main controls
│   │   ├── JobProgress.tsx        # Progress display
│   │   ├── ResultsViewer.tsx      # Results browser
│   │   └── ConfigModal.tsx        # Settings modal
│   └── types/
│       └── index.ts          # TypeScript definitions
├── package.json
├── tailwind.config.js
├── tsconfig.json
└── next.config.js
```

### Build for Production

```bash
npm run build
npm start
```

### Technologies Used

- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety and better DX
- **Tailwind CSS**: Utility-first styling
- **Heroicons**: Beautiful SVG icons
- **React Hot Toast**: Toast notifications
- **date-fns**: Date formatting utilities

## Troubleshooting

### Common Issues

**Python script not found:**
- Ensure the Python scraper is in the parent directory
- Check the path in `/api/scrape/route.ts`

**Port already in use:**
```bash
# Kill process on port 3000
npx kill-port 3000
```

**Dependencies not found:**
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Scraping jobs fail immediately:**
- Check that Python dependencies are installed in the parent directory
- Verify `python3` is available in your PATH
- Check the console for detailed error messages

### Debug Mode

Enable verbose logging by checking the browser console and API logs:

```bash
# In the browser console
localStorage.setItem('debug', 'true')

# View API logs
# Check the terminal where you ran `npm run dev`
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 