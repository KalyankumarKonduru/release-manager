import React from 'react'
import { TrendingUp, TrendingDown } from 'lucide-react'
import clsx from 'clsx'

interface MetricCardProps {
  label: string
  value: string | number
  trend?: number
  unit?: string
  icon?: React.ReactNode
  color?: 'indigo' | 'green' | 'blue' | 'purple'
}

export function MetricCard({
  label,
  value,
  trend,
  unit = '',
  icon,
  color = 'indigo',
}: MetricCardProps) {
  const colorClasses = {
    indigo: 'text-indigo-400',
    green: 'text-green-400',
    blue: 'text-blue-400',
    purple: 'text-purple-400',
  }

  const isTrendingUp = trend && trend > 0
  const isTrendingDown = trend && trend < 0

  return (
    <div className="card p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-gray-400 text-sm font-medium">{label}</p>
          <div className="mt-2 flex items-baseline gap-2">
            <p className={clsx('text-3xl font-bold', colorClasses[color])}>
              {value}
            </p>
            {unit && <span className="text-gray-500 text-sm">{unit}</span>}
          </div>
          {trend !== undefined && (
            <div className="mt-3 flex items-center gap-1">
              {isTrendingUp && <TrendingUp className="w-4 h-4 text-green-400" />}
              {isTrendingDown && <TrendingDown className="w-4 h-4 text-red-400" />}
              <span className={clsx('text-sm font-medium', {
                'text-green-400': isTrendingUp,
                'text-red-400': isTrendingDown,
                'text-gray-400': !isTrendingUp && !isTrendingDown,
              })}>
                {isTrendingUp ? '+' : ''}{trend}% from last period
              </span>
            </div>
          )}
        </div>
        {icon && <div className="ml-4 flex-shrink-0">{icon}</div>}
      </div>
    </div>
  )
}
