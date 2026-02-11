import React, { useState } from 'react'
import { Release } from '@/types'
import { StatusBadge } from './StatusBadge'
import { ChevronDown, ChevronUp, GitBranch, User, Calendar, Play, RotateCcw } from 'lucide-react'

interface ReleaseCardProps {
  release: Release
  onDeploy?: (releaseId: string) => void
  onRollback?: (releaseId: string) => void
  isLoading?: boolean
}

export function ReleaseCard({
  release,
  onDeploy,
  onRollback,
  isLoading = false,
}: ReleaseCardProps) {
  const [expanded, setExpanded] = useState(false)

  const statusMap = {
    draft: 'pending',
    pending: 'pending',
    deployed: 'success',
    failed: 'failed',
  } as const

  return (
    <div className="card overflow-hidden">
      <div
        className="p-6 cursor-pointer hover:bg-gray-700/50 transition-smooth"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold text-gray-100">
                v{release.version}
              </h3>
              <StatusBadge status={statusMap[release.status]} size="sm" />
            </div>
            <p className="text-sm text-gray-400 mt-2">
              {release.service.name}
            </p>
            <div className="flex flex-wrap gap-3 mt-4 text-sm">
              <div className="flex items-center gap-2 text-gray-400">
                <GitBranch className="w-4 h-4" />
                {release.branch}
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <User className="w-4 h-4" />
                {release.author.name}
              </div>
              <div className="flex items-center gap-2 text-gray-400">
                <Calendar className="w-4 h-4" />
                {new Date(release.created_at).toLocaleDateString()}
              </div>
            </div>
          </div>
          <button
            onClick={(e) => {
              e.stopPropagation()
              setExpanded(!expanded)
            }}
            className="ml-4 text-gray-400 hover:text-gray-200"
          >
            {expanded ? <ChevronUp /> : <ChevronDown />}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="border-t border-gray-700 bg-gray-900/50 p-6">
          <div className="space-y-4">
            {release.description && (
              <div>
                <p className="text-xs text-gray-400 font-medium mb-2">Description</p>
                <p className="text-sm text-gray-300">{release.description}</p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4 py-4 border-t border-gray-700">
              <div>
                <p className="text-xs text-gray-400 font-medium">Commit</p>
                <p className="text-sm text-gray-300 font-mono">
                  {release.commit_hash.substring(0, 7)}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-400 font-medium">Status</p>
                <p className="text-sm text-gray-300 capitalize">
                  {release.status}
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              {release.status !== 'deployed' && onDeploy && (
                <button
                  onClick={() => onDeploy(release.id)}
                  disabled={isLoading}
                  className="btn-primary flex-1 flex items-center justify-center gap-2"
                >
                  <Play className="w-4 h-4" />
                  Deploy
                </button>
              )}
              {release.status === 'deployed' && onRollback && (
                <button
                  onClick={() => onRollback(release.id)}
                  disabled={isLoading}
                  className="btn-danger flex-1 flex items-center justify-center gap-2"
                >
                  <RotateCcw className="w-4 h-4" />
                  Rollback
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
