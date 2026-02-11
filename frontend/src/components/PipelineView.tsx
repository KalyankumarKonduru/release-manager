import React from 'react'
import { StatusBadge } from './StatusBadge'
import { PipelineStage } from '@/types'
import { ChevronRight, CheckCircle2, AlertCircle, Clock } from 'lucide-react'

interface PipelineViewProps {
  stages: PipelineStage[]
  compact?: boolean
}

export function PipelineView({ stages, compact = false }: PipelineViewProps) {
  if (stages.length === 0) {
    return (
      <div className="text-gray-400 text-sm">No pipeline stages available</div>
    )
  }

  const getStageIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle2 className="w-5 h-5 text-green-400" />
      case 'failed':
        return <AlertCircle className="w-5 h-5 text-red-400" />
      case 'running':
        return <Clock className="w-5 h-5 text-blue-400 animate-spin" />
      default:
        return <Clock className="w-5 h-5 text-gray-500" />
    }
  }

  if (compact) {
    return (
      <div className="flex items-center gap-2">
        {stages.map((stage, index) => (
          <React.Fragment key={stage.id}>
            <div className="flex flex-col items-center gap-1">
              <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                stage.status === 'success' ? 'bg-green-900/30' :
                stage.status === 'failed' ? 'bg-red-900/30' :
                stage.status === 'running' ? 'bg-blue-900/30' :
                'bg-gray-800'
              }`}>
                {getStageIcon(stage.status)}
              </div>
              <span className="text-xs text-gray-400">{stage.name}</span>
            </div>
            {index < stages.length - 1 && (
              <ChevronRight className="w-4 h-4 text-gray-600 -mx-1" />
            )}
          </React.Fragment>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {stages.map((stage, index) => (
        <div key={stage.id}>
          <div className="flex items-start gap-4">
            <div className="flex-shrink-0">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                stage.status === 'success' ? 'bg-green-900/30' :
                stage.status === 'failed' ? 'bg-red-900/30' :
                stage.status === 'running' ? 'bg-blue-900/30' :
                'bg-gray-800'
              }`}>
                {getStageIcon(stage.status)}
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-3 mb-2">
                <h4 className="font-medium text-gray-100">{stage.name}</h4>
                <StatusBadge status={stage.status as any} size="sm" />
              </div>
              {stage.completed_at && stage.started_at && (
                <p className="text-xs text-gray-500">
                  Completed in{' '}
                  {Math.round(
                    (new Date(stage.completed_at).getTime() -
                      new Date(stage.started_at).getTime()) /
                      1000
                  )}{' '}
                  seconds
                </p>
              )}
            </div>
          </div>
          {index < stages.length - 1 && (
            <div className="ml-5 h-8 border-l border-gray-700" />
          )}
        </div>
      ))}
    </div>
  )
}
