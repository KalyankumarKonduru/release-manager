import React, { useState } from 'react'
import { useAuditLogs } from '@/hooks/useAnalytics'
import { AuditLogTable } from '@/components/AuditLogTable'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { Calendar, User, Zap } from 'lucide-react'

export default function AuditLogs() {
  const [page, setPage] = useState(1)
  const [sortField, setSortField] = useState<string>('created_at')
  const [sortDesc, setSortDesc] = useState(true)
  const [filters, setFilters] = useState({
    date_from: '',
    date_to: '',
    action: '',
    user_id: '',
  })

  const { data: auditLogs, isLoading } = useAuditLogs(page, 50, {
    action: filters.action || undefined,
    user_id: filters.user_id || undefined,
    date_from: filters.date_from || undefined,
    date_to: filters.date_to || undefined,
  })

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortDesc(!sortDesc)
    } else {
      setSortField(field)
      setSortDesc(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Audit Logs</h1>
        <p className="text-gray-400 mt-1">
          Track all actions and changes in the system
        </p>
      </div>

      {/* Filters */}
      <div className="card p-6 space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Date From */}
          <div>
            <label className="block text-xs text-gray-400 font-medium mb-2">
              <Calendar className="w-4 h-4 inline mr-1" />
              From Date
            </label>
            <input
              type="date"
              value={filters.date_from}
              onChange={(e) =>
                setFilters({ ...filters, date_from: e.target.value })
              }
              className="input-field text-sm"
            />
          </div>

          {/* Date To */}
          <div>
            <label className="block text-xs text-gray-400 font-medium mb-2">
              <Calendar className="w-4 h-4 inline mr-1" />
              To Date
            </label>
            <input
              type="date"
              value={filters.date_to}
              onChange={(e) =>
                setFilters({ ...filters, date_to: e.target.value })
              }
              className="input-field text-sm"
            />
          </div>

          {/* Action Type */}
          <div>
            <label className="block text-xs text-gray-400 font-medium mb-2">
              <Zap className="w-4 h-4 inline mr-1" />
              Action Type
            </label>
            <select
              value={filters.action}
              onChange={(e) =>
                setFilters({ ...filters, action: e.target.value })
              }
              className="input-field text-sm"
            >
              <option value="">All Actions</option>
              <option value="create">Create</option>
              <option value="update">Update</option>
              <option value="delete">Delete</option>
              <option value="deploy">Deploy</option>
              <option value="approve">Approve</option>
              <option value="reject">Reject</option>
            </select>
          </div>

          {/* User */}
          <div>
            <label className="block text-xs text-gray-400 font-medium mb-2">
              <User className="w-4 h-4 inline mr-1" />
              User
            </label>
            <input
              type="text"
              placeholder="User name or email"
              value={filters.user_id}
              onChange={(e) =>
                setFilters({ ...filters, user_id: e.target.value })
              }
              className="input-field text-sm"
            />
          </div>
        </div>

        {/* Reset button */}
        <div className="flex justify-end">
          <button
            onClick={() =>
              setFilters({
                date_from: '',
                date_to: '',
                action: '',
                user_id: '',
              })
            }
            className="text-sm text-indigo-400 hover:text-indigo-300 font-medium"
          >
            Reset Filters
          </button>
        </div>
      </div>

      {/* Audit logs table */}
      {isLoading ? (
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner text="Loading audit logs..." />
        </div>
      ) : auditLogs?.data && auditLogs.data.length > 0 ? (
        <div>
          <AuditLogTable
            logs={auditLogs.data}
            isLoading={isLoading}
            onSort={handleSort}
            sortField={sortField}
            sortDesc={sortDesc}
          />

          {/* Pagination */}
          {auditLogs.total_pages > 1 && (
            <div className="flex justify-center gap-2 mt-6">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="btn-secondary disabled:opacity-50"
              >
                Previous
              </button>
              <span className="px-4 py-2 text-gray-400">
                Page {page} of {auditLogs.total_pages}
              </span>
              <button
                onClick={() =>
                  setPage(Math.min(auditLogs.total_pages, page + 1))
                }
                disabled={page === auditLogs.total_pages}
                className="btn-secondary disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          title="No audit logs found"
          description="Audit logs will appear here as actions are performed in the system"
        />
      )}
    </div>
  )
}
