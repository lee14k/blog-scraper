import { NextRequest, NextResponse } from 'next/server'

interface ScrapeRequest {
  type: 'all' | 'interviewing-io' | 'nilmamano' | 'generic-blog' | 'pdf'
  config: {
    delay?: number
    maxRetries?: number
    timeout?: number
    maxChapters?: number
    outputDir?: string
    blogUrl?: string
    pdfUrl?: string
  }
  jobId: string
}

export async function POST(request: NextRequest) {
  try {
    const body: ScrapeRequest = await request.json()
    
    // Validate the request
    if (!body.type || !['all', 'interviewing-io', 'nilmamano', 'generic-blog', 'pdf'].includes(body.type)) {
      return NextResponse.json(
        { error: 'Invalid scrape type' },
        { status: 400 }
      )
    }

    if (!body.jobId) {
      return NextResponse.json(
        { error: 'Job ID is required' },
        { status: 400 }
      )
    }

    // For generic-blog, require blogUrl
    if (body.type === 'generic-blog' && !body.config?.blogUrl) {
      return NextResponse.json(
        { error: 'Blog URL is required for generic blog scraping' },
        { status: 400 }
      )
    }

    // For PDF, require pdfUrl
    if (body.type === 'pdf' && !body.config?.pdfUrl) {
      return NextResponse.json(
        { error: 'PDF URL is required for PDF scraping' },
        { status: 400 }
      )
    }

    console.log('Starting scrape job:', body)

    // Create a streaming response to simulate real-time progress
    const stream = new ReadableStream({
      start(controller) {
        let progress = 0

        // Send initial progress
        const sendProgress = (prog: number, message: string) => {
          controller.enqueue(new TextEncoder().encode(
            JSON.stringify({
              type: 'progress',
              progress: prog,
              message
            }) + '\n'
          ))
        }

        // Send error
        const sendError = (error: string) => {
          controller.enqueue(new TextEncoder().encode(
            JSON.stringify({
              type: 'error',
              error
            }) + '\n'
          ))
        }

        // Send completion with mock result
        const sendComplete = (result: any) => {
          controller.enqueue(new TextEncoder().encode(
            JSON.stringify({
              type: 'complete',
              result
            }) + '\n'
          ))
        }

        // Simulate the scraping process
        const interval = setInterval(() => {
          progress += Math.random() * 15 + 5 // Random progress between 5-20%
          
          if (progress < 30) {
            sendProgress(progress, `Initializing ${body.type} scraper...`)
          } else if (progress < 60) {
            sendProgress(progress, `Discovering content from ${body.type}...`)
          } else if (progress < 90) {
            sendProgress(progress, `Scraping articles and posts...`)
          } else if (progress < 100) {
            sendProgress(progress, `Processing and saving content...`)
          } else {
            clearInterval(interval)
            
            // Create mock result
            const mockResult = {
              id: `result_${Date.now()}`,
              jobId: body.jobId,
              type: body.type,
              success: true,
              sourceUrl: body.config?.blogUrl || body.config?.pdfUrl || `${body.type} source`,
              totalFound: Math.floor(Math.random() * 50) + 10,
              totalScraped: Math.floor(Math.random() * 50) + 10,
              totalEntries: Math.floor(Math.random() * 50) + 10,
              errors: [],
              scrapedAt: new Date(),
              metadata: {
                totalSources: 1,
                successfulSources: 1,
                totalErrors: 0
              },
              entries: [
                {
                  id: 'entry_1',
                  title: `Sample ${body.type} Article`,
                  content: `This is sample content scraped from ${body.type}. This would contain the actual article content in a real scenario.`,
                  url: `https://example.com/${body.type}/article1`,
                  publishedDate: new Date(),
                  author: 'Sample Author',
                  tags: [
                    { slug: 'tech', name: 'Technology' },
                    { slug: 'programming', name: 'Programming' }
                  ],
                  contentType: 'article',
                  sourceDomain: body.type === 'generic-blog' && body.config?.blogUrl 
                    ? new URL(body.config.blogUrl).hostname 
                    : `${body.type}.com`,
                  scrapedAt: new Date(),
                  metadata: {}
                }
              ]
            }

            sendComplete(mockResult)
            controller.close()
          }
        }, 1000) // Update every second

        // Handle cleanup if the client disconnects
        setTimeout(() => {
          if (!controller.desiredSize || controller.desiredSize <= 0) {
            clearInterval(interval)
          }
        }, 30000) // Max 30 seconds
      }
    })

    return new NextResponse(stream, {
      headers: {
        'Content-Type': 'text/plain',
        'Transfer-Encoding': 'chunked',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    })

  } catch (error) {
    console.error('Error starting scrape job:', error)
    return NextResponse.json(
      { error: 'Failed to start scraping job' },
      { status: 500 }
    )
  }
}

export async function GET() {
  // Return mock jobs for testing
  const mockJobs = [
    {
      id: 'job_1',
      type: 'interviewing-io',
      status: 'completed',
      progress: 100,
      startTime: new Date(Date.now() - 300000), // 5 minutes ago
      logs: [
        'Starting interviewing.io scraping...',
        'Found 25 articles',
        'Scraping article 1/25...',
        'Scraping article 25/25...',
        'Completed successfully'
      ],
      error: null
    }
  ]

  return NextResponse.json({
    success: true,
    jobs: mockJobs
  })
} 