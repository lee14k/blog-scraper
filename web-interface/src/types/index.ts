export interface ScrapeJob {
  id: string
  type: 'all' | 'interviewing-io' | 'nilmamano' | 'generic-blog' | 'pdf'
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  startTime: Date
  endTime?: Date
  config: ScrapeConfig
  logs: string[]
  error?: string
}

export interface ScrapeConfig {
  delay?: number
  maxRetries?: number
  timeout?: number
  maxChapters?: number
  blogUrl?: string
  pdfUrl?: string
  outputDir?: string
}

export interface ScrapeResult {
  id: string
  jobId: string
  type: string
  success: boolean
  sourceUrl: string
  totalFound: number
  totalScraped: number
  totalEntries: number
  errors: string[]
  scrapedAt: Date
  entries: KnowledgebaseEntry[]
  metadata: {
    totalSources: number
    successfulSources: number
    totalErrors: number
  }
}

export interface KnowledgebaseEntry {
  id: string
  title: string
  url: string
  sourceDomain: string
  content: string
  excerpt?: string
  contentType: string
  publishedDate?: Date
  modifiedDate?: Date
  author?: Author
  tags: Tag[]
  scrapedAt: Date
  metadata: Record<string, any>
}

export interface Author {
  name: string
  email?: string
  url?: string
}

export interface Tag {
  name: string
  slug: string
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface ScrapingProgress {
  jobId: string
  status: 'starting' | 'scraping' | 'processing' | 'saving' | 'completed' | 'error'
  progress: number
  currentStep: string
  totalSteps: number
  entriesFound: number
  errors: string[]
} 