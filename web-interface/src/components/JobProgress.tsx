'use client'

import React, { useState } from 'react'
import { ScrapeJob } from '@/types'

interface Props {
  job: ScrapeJob
  onRemove: () => void
}

export default function JobProgress({ job, onRemove }: Props) {
  const [showLogs, setShowLogs] = useState(false)

  const getStatusColor = (status: ScrapeJob['status']) => {
    switch (status) {
      case 'pending': return 'bg-yellow-500'
      case 'running': return 'bg-blue-500'
      case 'completed': return 'bg-green-500'
      case 'failed': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  const getStatusIcon = (status: ScrapeJob['status']) => {
    switch (status) {
      case 'pending': return '⏳'
      case 'running': return '🚀'
      case 'completed': return '✅'
      case 'failed': return '❌'
      default: return '⚪'
    }
  }

  const formatTimeAgo = (date: Date) => {
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  return (
    <div className="bg-white border rounded-lg p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="text-xl">{getStatusIcon(job.status)}</div>
          <div>
            <h4 className="font-medium text-gray-900 capitalize">
              {job.type.replace('-', ' ')} Scraping
            </h4>
            <p className="text-sm text-gray-500">
              Started {formatTimeAgo(job.startTime)}
            </p>
          </div>
        </div>
        
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowLogs(!showLogs)}
            className="p-1 text-gray-400 hover:text-gray-600"
          >
            {showLogs ? '🔼' : '🔽'}
          </button>
          
          {(job.status === 'completed' || job.status === 'failed') && (
            <button
              onClick={onRemove}
              className="p-1 text-gray-400 hover:text-red-600"
            >
              ❌
            </button>
          )}
        </div>
      </div>

      {/* Progress Bar */}
      {job.status === 'running' && (
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Progress</span>
            <span>{Math.round(job.progress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className={`h-2 rounded-full transition-all duration-300 ${
                job.progress > 0 ? 'progress-bar' : 'bg-gray-300'
              }`}
              style={{ width: `${job.progress}%` }}
            />
          </div>
        </div>
      )}

      {/* Error Display */}
      {job.error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md">
          <p className="text-sm text-red-800">{job.error}</p>
        </div>
      )}

      {/* Logs */}
      {showLogs && job.logs.length > 0 && (
        <div className="mt-4">
          <h5 className="text-sm font-medium text-gray-900 mb-2">Logs</h5>
          <div className="bg-gray-50 rounded-md p-3 max-h-48 overflow-y-auto">
            <div className="space-y-1">
              {job.logs.map((log, index) => (
                <div key={index} className="text-xs text-gray-600 font-mono">
                  {log}
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 