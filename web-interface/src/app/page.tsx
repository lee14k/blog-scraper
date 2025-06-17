'use client'

import React, { useState } from 'react'
import ScrapingDashboard from '@/components/ScrapingDashboard'
import ResultsViewer from '@/components/ResultsViewer'
import { ScrapeJob, ScrapeResult } from '@/types'

export default function HomePage() {
  const [activeJobs, setActiveJobs] = useState<ScrapeJob[]>([])
  const [completedJobs, setCompletedJobs] = useState<ScrapeResult[]>([])
  const [selectedResult, setSelectedResult] = useState<ScrapeResult | null>(null)

  const addJob = (job: ScrapeJob) => {
    setActiveJobs(prev => [...prev, job])
  }

  const updateJob = (jobId: string, updates: Partial<ScrapeJob>) => {
    setActiveJobs(prev => 
      prev.map(job => 
        job.id === jobId ? { ...job, ...updates } : job
      )
    )
  }

  const completeJob = (jobId: string, result: ScrapeResult) => {
    setActiveJobs(prev => prev.filter(job => job.id !== jobId))
    setCompletedJobs(prev => [result, ...prev])
  }

  const removeJob = (jobId: string) => {
    setActiveJobs(prev => prev.filter(job => job.id !== jobId))
  }

  return (
    <div className="space-y-8">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <span className="text-blue-600 text-xl">🚀</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Active Jobs</p>
              <p className="text-2xl font-bold text-gray-900">{activeJobs.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <span className="text-green-600 text-xl">✅</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Completed Jobs</p>
              <p className="text-2xl font-bold text-gray-900">{completedJobs.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-sm border">
          <div className="flex items-center">
            <div className="p-2 bg-purple-100 rounded-lg">
              <span className="text-purple-600 text-xl">📊</span>
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Entries</p>
              <p className="text-2xl font-bold text-gray-900">
                {completedJobs.reduce((sum, job) => sum + (job.totalEntries || 0), 0)}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Scraping Dashboard */}
        <div className="space-y-6">
          <ScrapingDashboard 
            onJobStart={addJob}
            onJobUpdate={updateJob}
            onJobComplete={completeJob}
            onJobRemove={removeJob}
            activeJobs={activeJobs}
          />
        </div>

        {/* Results Viewer */}
        <div className="space-y-6">
          <ResultsViewer 
            results={completedJobs}
            selectedResult={selectedResult}
            onResultSelect={setSelectedResult}
          />
        </div>
      </div>
    </div>
  )
} 