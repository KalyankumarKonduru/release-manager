import React, { useState } from 'react'
import { AuditLog } from '@/types'
import { formatDistanceToNow } from 'date-fns'
import { ChevronUp, ChevronDown, Download } from 'lucide-react'

interface AuditLogTableProps {
  logs: AuditLog[]
  isLoading?: boolean
  onSort?: (field: string) => void
  sortField?: string
  sortDesc?: boolean
}

export function AuditLogTable({
  logs,
  isLoading = false,
  onSort,
  sortField,
  sortDesc = false,
}: AuditLogTableProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null)

  const handleExportCSV = () => {
    const headers = ['User', 'Action', 'Resource', 'Date', 'Details']
    const rows = logs.map((log) => [
      log.user.name,
      log.action,
      `${log.resource_type}:${log.resource_id}`,
      new Date(log.created_at).toISOString(),
      JSON.stringify(log.changes || {}),
    ])

    const csv = [
      headers.join(','),
      ...rows.map((row) =>
        row
          .map((cell) => `"${String(cell).replace(/"/g, '""')}"`)
          .join(',')
      ),
    ].join('\n')

    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  if (isLoading) {
    return (
      <div className="card p-6 text-center">
        <p className="text-gray-400">Loading audit logs...</p>
      </div>
    )
  }

  if (logs.length === 0) {
    return (
      <div className="card p-6 text-center">
        <p className="text-gray-400">No audit logs found</p>
      </div>
    )
  }

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-700 bg-gray-900/50">
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => onSort?.('user')}
                  className="flex items-center gap-1 text-xs font-semibold text-gray-400 hover:text-gray-200"
                >
                  User
                  {sortField === 'user' &&
                    (sortDesc ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />)}
                </button>
              </th>
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => onSort?.('action')}
                  className="flex items-center gap-1 text-xs font-semibold text-gray-400 hover:text-gray-200"
                >
                  Action
                  {sortField === 'action' &&
                    (sortDesc ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />)}
                </button>
              </th>
              <th className="px-6 py-3 text-left">
                <button
                  onClick={() => onSort?.('resource')}
                  className="flex items-center gap-1 text-xs font-semibold text-gray-400 hover:text-gray-200"
                >
                  Resource
                  {sortField === 'resource' &&
                    (sortDesc ? <ChevronDown className="w-4 h-4" /> : <ChevronUp className="w-4 h-4" />)}
                </button>
              </th>
              <th className="px-6 py-3 text-left text-xs font-semibold text-gray-400">
                Timestamp
              </th>
              <th className="px-6 py-3 text-right text-xs font-semibold text-gray-400">
                Details
              </th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <React.Fragment key={log.id}>
                <tr className="border-b border-gray-800 hover:bg-gray-800/50 transition-smooth">
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-medium text-gray-100">{log.user.name}</p>
                      <p className="text-xs text-gray-500">{log.user.email}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className="inline-flex px-2 py-1 rounded-full text-xs font-medium bg-indigo-900/30 text-indigo-300">
                      {log.action}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-300">
                    {log.resource_type}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-400">
                    {formatDistanceToNow(new Date(log.created_at), { addSuffix: true })}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <button
                      onClick={() =>
                        setExpandedId(expandedId === log.id ? null : log.id)
                      }
                      className="text-indigo-400 hover:text-indigo-300 text-sm font-medium"
                    >
                      {expandedId === log.id ? 'Hide' : 'Show'}
                    </button>
                  </td>
                </tr>
                {expandedId === log.id && (
                  <tr className="bg-gray-900/50 border-b border-gray-800">
                    <td colSpan={5} className="px-6 py-4">
                      <div className="bg-gray-950 rounded-lg p-4 font-mono text-xs text-gray-300 overflow-auto max-h-64">
                        {log.changes && Object.keys(log.changes).length > 0 ? (
                          <pre>{JSON.stringify(log.changes, null, 2)}</pre>
                        ) : (
                          <p className="text-gray-500">No additional details</p>
                        )}
                      </div>
                    </td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
      <div className="border-t border-gray-700 px-6 py-4 flex justify-end">
        <button
          onClick={handleExportCSV}
          className="flex items-center gap-2 text-sm text-indigo-400 hover:text-indigo-300 font-medium"
        >
          <Download className="w-4 h-4" />
          Export CSV
        </button>
      </div>
    </div>
  )
}
