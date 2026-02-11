import React, { useState } from 'react'
import { Deployment } from '@/types'
import { StatusBadge } from './StatusBadge'
import { Check, X, MessageSquare } from 'lucide-react'

interface ApprovalCardProps {
  deployment: Deployment
  onApprove: (comment?: string) => void
  onReject: (comment?: string) => void
  isLoading?: boolean
}

export function ApprovalCard({
  deployment,
  onApprove,
  onReject,
  isLoading = false,
}: ApprovalCardProps) {
  const [comment, setComment] = useState('')
  const [showCommentInput, setShowCommentInput] = useState(false)

  const handleApprove = () => {
    onApprove(comment || undefined)
    setComment('')
    setShowCommentInput(false)
  }

  const handleReject = () => {
    onReject(comment || undefined)
    setComment('')
    setShowCommentInput(false)
  }

  return (
    <div className="card p-6">
      <div className="space-y-4">
        <div className="flex items-start justify-between">
          <div>
            <h4 className="font-semibold text-gray-100">
              {deployment.release.service.name} v{deployment.release.version}
            </h4>
            <p className="text-sm text-gray-400 mt-1">
              {deployment.environment.charAt(0).toUpperCase() +
                deployment.environment.slice(1)}{' '}
              Deployment
            </p>
          </div>
          <StatusBadge status="pending" />
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p className="text-gray-500">Requested by</p>
            <p className="text-gray-100 font-medium">
              {deployment.requested_by.name}
            </p>
          </div>
          <div>
            <p className="text-gray-500">Branch</p>
            <p className="text-gray-100 font-medium">{deployment.release.branch}</p>
          </div>
          <div>
            <p className="text-gray-500">Commit</p>
            <p className="text-gray-100 font-mono text-xs">
              {deployment.release.commit_hash.substring(0, 7)}
            </p>
          </div>
          <div>
            <p className="text-gray-500">Requested</p>
            <p className="text-gray-100 font-medium">
              {new Date(deployment.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>

        {deployment.release.description && (
          <div className="bg-gray-900 rounded-lg p-3">
            <p className="text-xs text-gray-400 font-medium mb-1">Description</p>
            <p className="text-sm text-gray-200">{deployment.release.description}</p>
          </div>
        )}

        {showCommentInput && (
          <div className="bg-gray-900 rounded-lg p-3">
            <label className="block text-xs text-gray-400 font-medium mb-2">
              <MessageSquare className="w-4 h-4 inline mr-1" />
              Add a comment
            </label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="input-field resize-none"
              placeholder="Add your approval/rejection comment..."
              rows={3}
            />
          </div>
        )}

        {!showCommentInput && (
          <button
            onClick={() => setShowCommentInput(true)}
            className="w-full text-left text-sm text-indigo-400 hover:text-indigo-300 font-medium"
          >
            <MessageSquare className="w-4 h-4 inline mr-2" />
            Add comment
          </button>
        )}

        <div className="flex gap-3">
          <button
            onClick={handleApprove}
            disabled={isLoading}
            className="btn-primary flex-1 flex items-center justify-center gap-2"
          >
            <Check className="w-4 h-4" />
            Approve
          </button>
          <button
            onClick={handleReject}
            disabled={isLoading}
            className="btn-danger flex-1 flex items-center justify-center gap-2"
          >
            <X className="w-4 h-4" />
            Reject
          </button>
        </div>
      </div>
    </div>
  )
}
