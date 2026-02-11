import React from 'react'
import { EnvironmentStatus, Environment } from '@/types'
import { StatusBadge } from './StatusBadge'
import { Activity } from 'lucide-react'

interface EnvironmentStatusProps {
  statuses: EnvironmentStatus[]
}

export function EnvironmentStatusComponent({
  statuses,
}: EnvironmentStatusProps) {
  const getHealthColor = (health: string) => {
    switch (health) {
      case 'healthy':
        return 'border-green-500/30 bg-green-500/5'
      case 'warning':
        return 'border-yellow-500/30 bg-yellow-500/5'
      case 'critical':
        return 'border-red-500/30 bg-red-500/5'
      default:
        return 'border-gray-700 bg-gray-800/50'
    }
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
      {statuses.map((status) => (
        <div
          key={status.environment}
          className={`card border-2 p-6 ${getHealthColor(status.health)}`}
        >
          <div className="flex items-start justify-between">
            <div>
              <h4 className="font-semibold text-gray-100 capitalize">
                {status.environment}
              </h4>
              <p className="text-xs text-gray-400 mt-1">
                Environment Status
              </p>
            </div>
            <StatusBadge
              status={
                status.health === 'healthy'
                  ? 'success'
                  : status.health === 'warning'
                    ? 'warning'
                    : 'failed'
              }
              size="sm"
            />
          </div>

          <div className="mt-6 space-y-3">
            <div className="flex items-center gap-3">
              <Activity className="w-4 h-4 text-blue-400" />
              <span className="text-sm text-gray-300">
                {status.uptime_percentage.toFixed(2)}% Uptime
              </span>
            </div>

            {status.last_deployment && (
              <div>
                <p className="text-xs text-gray-400 mb-1">Last Deployment</p>
                <p className="text-sm font-medium text-gray-200">
                  v{status.last_deployment.release.version}
                </p>
                <p className="text-xs text-gray-500">
                  {new Date(
                    status.last_deployment.deployed_at ||
                      status.last_deployment.created_at
                  ).toLocaleDateString()}
                </p>
              </div>
            )}
          </div>
        </div>
      ))}
    </div>
  )
}
