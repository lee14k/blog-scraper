'use client'

import React, { useState } from 'react'
import { ScrapeConfig } from '@/types'

interface Props {
  isOpen: boolean
  onClose: () => void
  config: ScrapeConfig
  onSave: (config: ScrapeConfig) => void
}

export default function ConfigModal({ isOpen, onClose, config, onSave }: Props) {
  const [localConfig, setLocalConfig] = useState<ScrapeConfig>(config)

  if (!isOpen) return null

  const handleSave = () => {
    onSave(localConfig)
    onClose()
  }

  const handleChange = (field: keyof ScrapeConfig, value: any) => {
    setLocalConfig(prev => ({ ...prev, [field]: value }))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Scraping Configuration</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            ❌
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Delay Between Requests (seconds)
            </label>
            <input
              type="number"
              step="0.1"
              min="0.1"
              value={localConfig.delay || 1.0}
              onChange={(e) => handleChange('delay', parseFloat(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max Retries
            </label>
            <input
              type="number"
              min="1"
              max="10"
              value={localConfig.maxRetries || 3}
              onChange={(e) => handleChange('maxRetries', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Timeout (seconds)
            </label>
            <input
              type="number"
              min="10"
              max="300"
              value={localConfig.timeout || 30}
              onChange={(e) => handleChange('timeout', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Max PDF Chapters
            </label>
            <input
              type="number"
              min="1"
              max="50"
              value={localConfig.maxChapters || 8}
              onChange={(e) => handleChange('maxChapters', parseInt(e.target.value))}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Output Directory
            </label>
            <input
              type="text"
              value={localConfig.outputDir || 'output'}
              onChange={(e) => handleChange('outputDir', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        <div className="flex justify-end space-x-3 mt-6 pt-4 border-t">
          <button
            onClick={onClose}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            Save Configuration
          </button>
        </div>
      </div>
    </div>
  )
} 