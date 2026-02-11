import React, { useState } from 'react'
import { Service } from '@/types'
import { StatusBadge } from '@/components/StatusBadge'
import { EmptyState } from '@/components/EmptyState'
import { ExternalLink, Plus } from 'lucide-react'

// Mock data for services
const mockServices: Service[] = [
  {
    id: '1',
    name: 'API Gateway',
    description: 'Central API routing and authentication',
    repository_url: 'https://github.com/example/api-gateway',
    team_id: '1',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '2',
    name: 'Web Frontend',
    description: 'React-based user interface',
    repository_url: 'https://github.com/example/web-frontend',
    team_id: '1',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '3',
    name: 'Database Service',
    description: 'PostgreSQL database and migrations',
    repository_url: 'https://github.com/example/db-service',
    team_id: '1',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '4',
    name: 'Notification Service',
    description: 'Email and push notifications',
    repository_url: 'https://github.com/example/notifications',
    team_id: '1',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

export default function Services() {
  const [services] = useState<Service[]>(mockServices)
  const [searchQuery, setSearchQuery] = useState('')

  const filteredServices = services.filter((service) =>
    service.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    service.description?.toLowerCase().includes(searchQuery.toLowerCase())
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-100">Services</h1>
          <p className="text-gray-400 mt-1">
            Manage services and track their deployments
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          New Service
        </button>
      </div>

      {/* Search */}
      <div className="card p-6">
        <input
          type="text"
          placeholder="Search services..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="input-field w-full"
        />
      </div>

      {/* Services grid */}
      {filteredServices.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredServices.map((service) => (
            <div key={service.id} className="card p-6">
              <div className="flex items-start justify-between mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-100">
                    {service.name}
                  </h3>
                  <p className="text-sm text-gray-400 mt-1">
                    {service.description}
                  </p>
                </div>
                <StatusBadge status="success" size="sm" />
              </div>

              <div className="space-y-4 py-4 border-t border-gray-700">
                {/* Repository */}
                <div>
                  <p className="text-xs text-gray-400 font-medium mb-1">
                    Repository
                  </p>
                  <a
                    href={service.repository_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-sm text-indigo-400 hover:text-indigo-300 flex items-center gap-1"
                  >
                    View on GitHub
                    <ExternalLink className="w-3 h-3" />
                  </a>
                </div>

                {/* Last deployment */}
                <div>
                  <p className="text-xs text-gray-400 font-medium mb-1">
                    Last Deployment
                  </p>
                  <p className="text-sm text-gray-300">v1.2.0 to Production</p>
                  <p className="text-xs text-gray-500 mt-1">2 days ago</p>
                </div>

                {/* Action buttons */}
                <div className="flex gap-2 pt-4 border-t border-gray-700">
                  <button className="btn-secondary flex-1 text-sm">
                    View Releases
                  </button>
                  <button className="btn-primary flex-1 text-sm">
                    Deploy
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          title="No services found"
          description="Create your first service to get started"
          action={{
            label: 'Create Service',
            onClick: () => {},
          }}
        />
      )}
    </div>
  )
}
