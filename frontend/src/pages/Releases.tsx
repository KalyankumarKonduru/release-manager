import React, { useState } from 'react'
import { useReleases, useDeployRelease } from '@/hooks/useReleases'
import { ReleaseCard } from '@/components/ReleaseCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import { Plus, Search } from 'lucide-react'

export default function Releases() {
  const [page, setPage] = useState(1)
  const [filters, setFilters] = useState<{
    status?: string
    search?: string
  }>({})
  const [searchInput, setSearchInput] = useState('')

  const { data: releases, isLoading } = useReleases(page, 20, filters)
  const deployMutation = useDeployRelease()

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    setFilters({ ...filters, search: searchInput })
  }

  const handleStatusFilter = (status: string) => {
    setPage(1)
    setFilters({
      ...filters,
      status: status === 'all' ? undefined : status,
    })
  }

  const handleDeploy = async (releaseId: string) => {
    try {
      await deployMutation.mutateAsync({
        releaseId,
        environment: 'staging',
      })
    } catch (error) {
      console.error('Deploy failed:', error)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-100">Releases</h1>
          <p className="text-gray-400 mt-1">
            Manage and deploy your service releases
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          New Release
        </button>
      </div>

      {/* Filters */}
      <div className="card p-6">
        <div className="flex flex-col md:flex-row gap-4">
          {/* Search */}
          <form onSubmit={handleSearch} className="flex-1">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search releases..."
                value={searchInput}
                onChange={(e) => setSearchInput(e.target.value)}
                className="input-field pl-10 w-full"
              />
            </div>
          </form>

          {/* Status filter */}
          <div className="flex gap-2">
            {['all', 'draft', 'pending', 'deployed', 'failed'].map(
              (status) => (
                <button
                  key={status}
                  onClick={() => handleStatusFilter(status)}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-smooth ${
                    filters.status === (status === 'all' ? undefined : status) ||
                    (!filters.status && status === 'all')
                      ? 'bg-indigo-600 text-white'
                      : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                  }`}
                >
                  {status.charAt(0).toUpperCase() + status.slice(1)}
                </button>
              )
            )}
          </div>
        </div>
      </div>

      {/* Releases list */}
      {isLoading ? (
        <div className="flex items-center justify-center h-96">
          <LoadingSpinner text="Loading releases..." />
        </div>
      ) : releases && releases.data.length > 0 ? (
        <div className="space-y-4">
          {releases.data.map((release) => (
            <ReleaseCard
              key={release.id}
              release={release}
              onDeploy={handleDeploy}
              isLoading={deployMutation.isPending}
            />
          ))}

          {/* Pagination */}
          {releases.total_pages > 1 && (
            <div className="flex justify-center gap-2 mt-6">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="btn-secondary disabled:opacity-50"
              >
                Previous
              </button>
              <span className="px-4 py-2 text-gray-400">
                Page {page} of {releases.total_pages}
              </span>
              <button
                onClick={() =>
                  setPage(Math.min(releases.total_pages, page + 1))
                }
                disabled={page === releases.total_pages}
                className="btn-secondary disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </div>
      ) : (
        <EmptyState
          title="No releases found"
          description="Create your first release to get started"
          action={{
            label: 'Create Release',
            onClick: () => {},
          }}
        />
      )}
    </div>
  )
}
