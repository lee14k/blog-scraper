'use client'

import React, { useState } from 'react'
import { toast } from 'react-hot-toast'
import { ScrapeJob, ScrapeConfig } from '@/types'
import JobProgress from './JobProgress'
import ConfigModal from './ConfigModal'

interface Props {
  onJobStart: (job: ScrapeJob) => void
  onJobUpdate: (jobId: string, updates: Partial<ScrapeJob>) => void
  onJobComplete: (jobId: string, result: any) => void
  onJobRemove: (jobId: string) => void
  activeJobs: ScrapeJob[]
}

export default function ScrapingDashboard({ 
  onJobStart, 
  onJobUpdate, 
  onJobComplete, 
  onJobRemove,
  activeJobs 
}: Props) {
  const [showConfig, setShowConfig] = useState(false)
  const [defaultConfig, setDefaultConfig] = useState<ScrapeConfig>({
    delay: 1.0,
    maxRetries: 3,
    timeout: 30,
    maxChapters: 8,
    outputDir: 'output'
  })

  const startScrapeJob = async (
    type: ScrapeJob['type'], 
    config: ScrapeConfig = defaultConfig
  ) => {
    const jobId = `job_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    const job: ScrapeJob = {
      id: jobId,
      type,
      status: 'pending',
      progress: 0,
      startTime: new Date(),
      config,
      logs: []
    }

    onJobStart(job)
    
    try {
      // Update job status to running
      onJobUpdate(jobId, { status: 'running', logs: ['Starting scrape job...'] })

      // Map job types to API endpoints and request formats
      let endpoint = ''
      let requestBody = {}

      switch (type) {
        case 'all':
          endpoint = '/scrape/all'
          requestBody = {
            google_drive_pdf_url: config.pdfUrl || null,
            config: {
              delay_between_requests: config.delay,
              max_retries: config.maxRetries,
              timeout: config.timeout
            }
          }
          break
        
        case 'interviewing-io':
          endpoint = '/scrape/interviewing-io/all'
          requestBody = {
            config: {
              delay_between_requests: config.delay,
              max_retries: config.maxRetries,
              timeout: config.timeout
            }
          }
          break
        
        case 'nilmamano':
          endpoint = '/scrape/nilmamano'
          requestBody = {
            config: {
              delay_between_requests: config.delay,
              max_retries: config.maxRetries,
              timeout: config.timeout
            }
          }
          break
        
        case 'generic-blog':
          if (!config.blogUrl) {
            throw new Error('Blog URL is required for generic blog scraping')
          }
          endpoint = '/scrape/generic-blog'
          requestBody = {
            blog_url: config.blogUrl,
            config: {
              delay_between_requests: config.delay,
              max_retries: config.maxRetries,
              timeout: config.timeout
            }
          }
          break
        
        case 'pdf':
          if (!config.pdfUrl) {
            throw new Error('PDF URL or path is required for PDF processing')
          }
          endpoint = '/scrape/pdf'
          requestBody = {
            pdf_url_or_path: config.pdfUrl,
            max_chapters: config.maxChapters || 8,
            config: {
              delay_between_requests: config.delay,
              max_retries: config.maxRetries,
              timeout: config.timeout
            }
          }
          break
        
        default:
          throw new Error(`Unknown job type: ${type}`)
      }

      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`HTTP error! status: ${response.status}, message: ${errorText}`)
      }

      const result = await response.json()
      
      // Update progress to 100% and mark as completed
      onJobUpdate(jobId, { 
        progress: 100,
        status: 'completed',
        logs: [...job.logs, 'Scraping completed successfully!']
      })
      
      onJobComplete(jobId, result)
      toast.success(`${type} scraping completed successfully! Scraped ${result.total_scraped || 'N/A'} items.`)

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error'
      onJobUpdate(jobId, { 
        status: 'failed', 
        error: errorMessage,
        logs: [...job.logs, `Error: ${errorMessage}`]
      })
      toast.error(`Failed to start scraping: ${errorMessage}`)
    }
  }

  const scrapeButtons = [
    {
      id: 'all',
      title: 'Scrape All Sources',
      description: 'Scrape interviewing.io, nilmamano.com, and PDF if provided',
      icon: '🚀',
      color: 'bg-blue-500 hover:bg-blue-600',
      action: () => startScrapeJob('all')
    },
    {
      id: 'interviewing-io',
      title: 'interviewing.io',
      description: 'Blog posts, company guides, and interview guides',
      icon: '📄',
      color: 'bg-green-500 hover:bg-green-600',
      action: () => startScrapeJob('interviewing-io')
    },
    {
      id: 'nilmamano',
      title: 'Nil Mamano DSA',
      description: 'Data structures and algorithms blog posts',
      icon: '🟣',
      color: 'bg-purple-500 hover:bg-purple-600',
      action: () => startScrapeJob('nilmamano')
    },
    {
      id: 'generic-blog',
      title: 'Generic Blog',
      description: 'Scrape any blog URL',
      icon: '🌐',
      color: 'bg-orange-500 hover:bg-orange-600',
      action: () => {
        const blogUrl = prompt('Enter blog URL:')
        if (blogUrl) {
          startScrapeJob('generic-blog', { ...defaultConfig, blogUrl })
        }
      }
    },
    {
      id: 'pdf',
      title: 'PDF Document',
      description: 'Extract chapters from PDF (local or Google Drive)',
      icon: '📄',
      color: 'bg-red-500 hover:bg-red-600',
      action: () => {
        const pdfUrl = prompt('Enter PDF path or Google Drive URL:')
        if (pdfUrl) {
          startScrapeJob('pdf', { ...defaultConfig, pdfUrl })
        }
      }
    }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">Scraping Operations</h2>
        <button
          onClick={() => setShowConfig(true)}
          className="flex items-center px-3 py-2 text-sm text-gray-600 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
        >
          ⚙️ Configure
        </button>
      </div>

      {/* Quick Action Buttons */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {scrapeButtons.map((button) => (
          <button
            key={button.id}
            onClick={button.action}
            disabled={activeJobs.some(job => job.type === button.id && job.status === 'running')}
            className={`
              ${button.color} text-white p-4 rounded-lg shadow-sm hover:shadow-md 
              transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed
              flex items-start space-x-3
            `}
          >
            <span className="text-2xl">{button.icon}</span>
            <div className="text-left">
              <h3 className="font-medium">{button.title}</h3>
              <p className="text-sm opacity-90">{button.description}</p>
            </div>
          </button>
        ))}
      </div>

      {/* Active Jobs */}
      {activeJobs.length > 0 && (
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-900">Active Jobs</h3>
          {activeJobs.map((job) => (
            <JobProgress 
              key={job.id} 
              job={job} 
              onRemove={() => onJobRemove(job.id)}
            />
          ))}
        </div>
      )}

      {/* Configuration Modal */}
      <ConfigModal
        isOpen={showConfig}
        onClose={() => setShowConfig(false)}
        config={defaultConfig}
        onSave={setDefaultConfig}
      />
    </div>
  )
} 