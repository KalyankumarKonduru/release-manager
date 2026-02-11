import React from 'react'
import { Deployment } from '@/types'
import { formatDistanceToNow } from 'date-fns'
import { Clock, CheckCircle2, AlertCircle } from 'lucide-react'

interface DeploymentTimelineProps {
  deployments: Deployment[]
}

export function DeploymentTimeline({ deployments }: DeploymentTimelineProps) {
  if (deployments.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-400 text-sm">No deployments yet</p>
      </div>
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-green-400" />
      case 'failed':
      case 'rolled_back':
        return <AlertCircle className="w-5 h-5 text-red-400" />
      default:
        return <Clock className="w-5 h-5 text-blue-400" />
    }
  }

  return (
    <div className="space-y-4">
      {deployments.map((deployment, index) => (
        <div key={deployment.id} className="relative">
          <div className="flex gap-4">
            <div className="relative flex flex-col items-center">
              <div className="w-10 h-10 rounded-full bg-gray-800 flex items-center justify-center">
                {getStatusIcon(deployment.status)}
              </div>
              {index < deployments.length - 1 && (
                <div className="w-0.5 h-12 bg-gray-700 my-2" />
              )}
            </div>
            <div className="flex-1 pb-4">
              <div className="flex items-start justify-between">
                <div>
                  <p className="font-medium text-gray-100">
                    {deployment.release.service.name} v{deployment.release.version}
                  </p>
                  <p className="text-sm text-gray-400 mt-0.5">
                    {deployment.environment.charAt(0).toUpperCase() +
                      deployment.environment.slice(1)}{' '}
                    • {deployment.status.charAt(0).toUpperCase() + deployment.status.slice(1)}
                  </p>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                {formatDistanceToNow(new Date(deployment.created_at), { addSuffix: true })}
              </p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
