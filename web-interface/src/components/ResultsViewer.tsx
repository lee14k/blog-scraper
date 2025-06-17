'use client'

import React from 'react'
import { ScrapeResult } from '@/types'

interface Props {
  results: ScrapeResult[]
  selectedResult: ScrapeResult | null
  onResultSelect: (result: ScrapeResult) => void
}

const formatTimeAgo = (date: Date | string) => {
  const now = new Date()
  const dateObj = typeof date === 'string' ? new Date(date) : date
  const diffMs = now.getTime() - dateObj.getTime()
  const diffMins = Math.floor(diffMs / 60000)
  
  if (diffMins < 1) return 'just now'
  if (diffMins < 60) return `${diffMins}m ago`
  const diffHours = Math.floor(diffMins / 60)
  if (diffHours < 24) return `${diffHours}h ago`
  const diffDays = Math.floor(diffHours / 24)
  return `${diffDays}d ago`
}

export default function ResultsViewer({ results, selectedResult, onResultSelect }: Props) {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-gray-900">Results</h2>
      
      {results.length === 0 ? (
        <div className="bg-white border-2 border-dashed border-gray-300 rounded-lg p-8 text-center">
          <div className="text-gray-400 text-6xl mb-4">📊</div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No results yet</h3>
          <p className="text-gray-500">
            Start a scraping job to see results here
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Results List */}
          <div className="bg-white border rounded-lg divide-y">
            {results.map((result) => (
              <div
                key={result.id}
                className={`p-4 cursor-pointer hover:bg-gray-50 transition-colors ${
                  selectedResult?.id === result.id ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
                }`}
                onClick={() => onResultSelect(result)}
              >
                <div className="flex justify-between items-start">
                  <div>
                    <h4 className="font-medium text-gray-900 capitalize">
                      {result.type.replace('-', ' ')} Results
                    </h4>
                    <p className="text-sm text-gray-500">
                      {result.totalEntries} entries • {formatTimeAgo(result.scrapedAt)}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    {result.success ? (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        ✅ Success
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                        ❌ Failed
                      </span>
                    )}
                  </div>
                </div>
                
                {result.errors.length > 0 && (
                  <div className="mt-2">
                    <p className="text-xs text-red-600">
                      {result.errors.length} error(s)
                    </p>
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Selected Result Details */}
          {selectedResult && (
            <div className="bg-white border rounded-lg p-6">
              <div className="mb-4">
                <h3 className="text-lg font-semibold text-gray-900 capitalize">
                  {selectedResult.type.replace('-', ' ')} - {selectedResult.totalEntries} Entries
                </h3>
                <p className="text-sm text-gray-500">
                  Source: {selectedResult.sourceUrl}
                </p>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {selectedResult.totalFound}
                  </div>
                  <div className="text-sm text-gray-600">Found</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {selectedResult.totalScraped}
                  </div>
                  <div className="text-sm text-gray-600">Scraped</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded-lg">
                  <div className="text-2xl font-bold text-gray-900">
                    {selectedResult.errors.length}
                  </div>
                  <div className="text-sm text-gray-600">Errors</div>
                </div>
              </div>

              {/* Sample Entries */}
              {selectedResult.entries.length > 0 && (
                <div>
                  <h4 className="text-md font-medium text-gray-900 mb-3">
                    Sample Entries ({Math.min(3, selectedResult.entries.length)} of {selectedResult.entries.length})
                  </h4>
                  <div className="space-y-3">
                    {selectedResult.entries.slice(0, 3).map((entry) => (
                      <div key={entry.id} className="border rounded-lg p-4 bg-gray-50">
                        <h5 className="font-medium text-gray-900 mb-1">{entry.title}</h5>
                        <p className="text-sm text-gray-600 mb-2">
                          {entry.sourceDomain} • {entry.contentType}
                        </p>
                        <p className="text-sm text-gray-700 line-clamp-2">
                          {entry.content.substring(0, 200)}...
                        </p>
                        <div className="mt-2 flex flex-wrap gap-1">
                          {entry.tags.slice(0, 3).map((tag) => (
                            <span 
                              key={tag.slug}
                              className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                            >
                              {tag.name}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Download Button */}
              <div className="mt-6 pt-4 border-t">
                <button
                  onClick={() => {
                    const dataStr = JSON.stringify(selectedResult, null, 2)
                    const dataBlob = new Blob([dataStr], { type: 'application/json' })
                    const url = URL.createObjectURL(dataBlob)
                    const link = document.createElement('a')
                    link.href = url
                    link.download = `scrape-results-${selectedResult.type}-${Date.now()}.json`
                    link.click()
                    URL.revokeObjectURL(url)
                  }}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  📥 Download Results
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
} 