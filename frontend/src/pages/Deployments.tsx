import React, { useState } from 'react'
import { useDeployments, useApproveDeployment, useRejectDeployment, useRollbackDeployment } from '@/hooks/useDeployments'
import { ApprovalCard } from '@/components/ApprovalCard'
import { PipelineView } from '@/components/PipelineView'
import { StatusBadge } from '@/components/StatusBadge'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { Deployment } from '@/types'
import { AlertCircle, ChevronDown, ChevronUp } from 'lucide-react'

export default function Deployments() {
  const [page, setPage] = useState(1)
  const [expandedId, setExpandedId] = useState<string | null>(null)
  const [filters, setFilters] = useState<{
    status?: string
    environment?: string
  }>({})

  const { data: deployments, isLoading } = useDeployments(page, 20, filters)
  const approveMutation = useApproveDeployment()
  const rejectMutation = useRejectDeployment()
  const rollbackMutation = useRollbackDeployment()

  const handleApprove = async (deploymentId: string, comment?: string) => {
    try {
      await approveMutation.mutateAsync({ deploymentId, comment })
    } catch (error) {
      console.error('Approval failed:', error)
    }
  }

  const handleReject = async (deploymentId: string, comment?: string) => {
    try {
      await rejectMutation.mutateAsync({ deploymentId, comment })
    } catch (error) {
      console.error('Rejection failed:', error)
    }
  }

  const handleRollback = async (deploymentId: string) => {
    try {
      await rollbackMutation.mutateAsync({
        deploymentId,
        reason: 'Manual rollback',
      })
    } catch (error) {
      console.error('Rollback failed:', error)
    }
  }

  const pendingApprovals = deployments?.data.filter(
    (d) => d.status === 'pending'
  ) || []

  const allDeployments = deployments?.data || []

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Deployments</h1>
        <p className="text-gray-400 mt-1">
          Manage deployments and approvals across environments
        </p>
      </div>

      {/* Status filters */}
      <div className="card p-6">
        <div className="flex flex-wrap gap-2">
          {['all', 'pending', 'approved', 'in_progress', 'success', 'failed'].map(
            (status) => (
              <button
                key={status}
                onClick={() => {
                  setPage(1)
                  setFilters({
                    ...filters,
                    status: status === 'all' ? undefined : status,
                  })
                }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-smooth ${
                  filters.status === (status === 'all' ? undefined : status) ||
                  (!filters.status && status === 'all')
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                {status.charAt(0).toUpperCase() + status.slice(1).replace('_', ' ')}
              </button>
            )
          )}
        </div>
      </div>

      {/* Pending approvals section */}
      {pendingApprovals.length > 0 && (
        <div>
          <h2 className="text-xl font-semibold text-gray-100 mb-4 flex items-center gap-2">
            <AlertCircle className="w-5 h-5 text-yellow-400" />
            Pending Approvals ({pendingApprovals.length})
          </h2>
          <div className="space-y-4">
            {pendingApprovals.map((deployment) => (
              <ApprovalCard
                key={deployment.id}
                deployment={deployment}
                onApprove={(comment) => handleApprove(deployment.id, comment)}
                onReject={(comment) => handleReject(deployment.id, comment)}
                isLoading={approveMutation.isPending || rejectMutation.isPending}
              />
            ))}
          </div>
        </div>
      )}

      {/* All deployments */}
      <div>
        <h2 className="text-xl font-semibold text-gray-100 mb-4">
          All Deployments
        </h2>

        {isLoading ? (
          <div className="flex items-center justify-center h-96">
            <LoadingSpinner text="Loading deployments..." />
          </div>
        ) : allDeployments.length > 0 ? (
          <div className="space-y-3">
            {allDeployments.map((deployment: Deployment) => (
              <div key={deployment.id} className="card overflow-hidden">
                <div
                  className="p-6 cursor-pointer hover:bg-gray-700/50 transition-smooth"
                  onClick={() =>
                    setExpandedId(
                      expandedId === deployment.id ? null : deployment.id
                    )
                  }
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-lg font-semibold text-gray-100">
                          {deployment.release.service.name} v{deployment.release.version}
                        </h3>
                        <StatusBadge status={deployment.status as any} size="sm" />
                      </div>
                      <p className="text-sm text-gray-400">
                        {deployment.environment.toUpperCase()} • Requested by{' '}
                        {deployment.requested_by.name}
                      </p>
                    </div>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        setExpandedId(
                          expandedId === deployment.id ? null : deployment.id
                        )
                      }}
                      className="text-gray-400"
                    >
                      {expandedId === deployment.id ? (
                        <ChevronUp />
                      ) : (
                        <ChevronDown />
                      )}
                    </button>
                  </div>
                </div>

                {expandedId === deployment.id && (
                  <div className="border-t border-gray-700 bg-gray-900/50 p-6">
                    <div className="space-y-6">
                      {/* Pipeline stages */}
                      {deployment.pipeline_stages && deployment.pipeline_stages.length > 0 && (
                        <div>
                          <h4 className="font-semibold text-gray-100 mb-4">
                            Pipeline Progress
                          </h4>
                          <PipelineView
                            stages={deployment.pipeline_stages}
                            compact={false}
                          />
                        </div>
                      )}

                      {/* Deployment info */}
                      <div className="grid grid-cols-2 gap-4 py-4 border-t border-gray-700">
                        <div>
                          <p className="text-xs text-gray-400 font-medium">
                            Commit
                          </p>
                          <p className="text-sm text-gray-300 font-mono mt-1">
                            {deployment.release.commit_hash.substring(0, 7)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-400 font-medium">
                            Branch
                          </p>
                          <p className="text-sm text-gray-300 mt-1">
                            {deployment.release.branch}
                          </p>
                        </div>
                      </div>

                      {/* Approval info */}
                      {deployment.approved_by && (
                        <div className="py-4 border-t border-gray-700">
                          <p className="text-xs text-gray-400 font-medium mb-1">
                            Approved by
                          </p>
                          <p className="text-sm text-gray-300">
                            {deployment.approved_by.name}
                          </p>
                          {deployment.approval_comment && (
                            <p className="text-sm text-gray-400 mt-2">
                              "{deployment.approval_comment}"
                            </p>
                          )}
                        </div>
                      )}

                      {/* Action buttons */}
                      {deployment.status === 'success' && (
                        <div className="flex gap-2 pt-2 border-t border-gray-700">
                          <button
                            onClick={() => handleRollback(deployment.id)}
                            className="btn-danger flex-1"
                          >
                            Rollback
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            title="No deployments found"
            description="Start by creating a release and deploying it to an environment"
          />
        )}
      </div>
    </div>
  )
}
