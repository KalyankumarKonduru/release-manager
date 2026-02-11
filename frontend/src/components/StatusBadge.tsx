import React from 'react'
import clsx from 'clsx'

interface StatusBadgeProps {
  status: 'success' | 'failed' | 'running' | 'pending' | 'approved' | 'rejected' | 'warning'
  text?: string
  size?: 'sm' | 'md'
}

export function StatusBadge({ status, text, size = 'md' }: StatusBadgeProps) {
  const statusConfig = {
    success: {
      bg: 'bg-green-900/30',
      text: 'text-green-400',
      dot: 'bg-green-500',
    },
    failed: {
      bg: 'bg-red-900/30',
      text: 'text-red-400',
      dot: 'bg-red-500',
    },
    running: {
      bg: 'bg-blue-900/30',
      text: 'text-blue-400',
      dot: 'bg-blue-500 animate-pulse',
    },
    pending: {
      bg: 'bg-yellow-900/30',
      text: 'text-yellow-400',
      dot: 'bg-yellow-500',
    },
    approved: {
      bg: 'bg-emerald-900/30',
      text: 'text-emerald-400',
      dot: 'bg-emerald-500',
    },
    rejected: {
      bg: 'bg-rose-900/30',
      text: 'text-rose-400',
      dot: 'bg-rose-500',
    },
    warning: {
      bg: 'bg-orange-900/30',
      text: 'text-orange-400',
      dot: 'bg-orange-500',
    },
  }

  const config = statusConfig[status]
  const paddingClasses = size === 'sm' ? 'px-2 py-1 text-xs' : 'px-3 py-1.5 text-sm'

  return (
    <div
      className={clsx(
        'inline-flex items-center gap-2 rounded-full font-medium',
        config.bg,
        config.text,
        paddingClasses
      )}
    >
      <div className={clsx('w-2 h-2 rounded-full', config.dot)} />
      {text || status.charAt(0).toUpperCase() + status.slice(1)}
    </div>
  )
}
