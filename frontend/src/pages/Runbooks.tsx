import React, { useState } from 'react'
import { Runbook } from '@/types'
import { EmptyState } from '@/components/EmptyState'
import { Search, Plus, Tag, User, Calendar } from 'lucide-react'

// Mock runbooks data
const mockRunbooks: Runbook[] = [
  {
    id: '1',
    title: 'Database Connection Timeout',
    description: 'Steps to diagnose and resolve database connection timeouts',
    category: 'Troubleshooting',
    content: `# Database Connection Timeout Resolution

## Overview
This runbook provides steps to diagnose and resolve database connection timeout issues.

## Symptoms
- Application receives timeout errors when connecting to database
- Connection pool is exhausted
- Slow query performance

## Diagnosis
1. Check database server status and connectivity
2. Verify connection pool configuration
3. Review active connections using:
   \`\`\`sql
   SELECT * FROM pg_stat_activity;
   \`\`\`
4. Check logs for slow queries

## Resolution
1. Increase connection pool size if needed
2. Identify and kill idle connections
3. Optimize slow queries
4. Add database indexes if needed
5. Consider connection pooling middleware`,
    author_id: '1',
    author: {
      id: '1',
      email: 'admin@example.com',
      name: 'Admin User',
      role: 'admin',
      team_id: '1',
      created_at: new Date().toISOString(),
    },
    tags: ['database', 'performance', 'troubleshooting'],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '2',
    title: 'Production Incident Response',
    description: 'General procedures for responding to production incidents',
    category: 'Incident Management',
    content: `# Production Incident Response

## Incident Severity Levels
- **Critical (P1)**: Service is down or severely degraded
- **High (P2)**: Significant functionality impacted
- **Medium (P3)**: Minor impact to users
- **Low (P4)**: No user impact

## Response Steps
1. **Assess**: Determine severity level and impact scope
2. **Notify**: Alert on-call team and stakeholders
3. **Investigate**: Gather logs, metrics, and system state
4. **Mitigate**: Take immediate action to reduce impact
5. **Resolve**: Implement permanent fix
6. **Review**: Document and conduct post-mortem

## Escalation Path
- On-call Engineer → Team Lead → Engineering Manager → VP Engineering`,
    author_id: '1',
    author: {
      id: '1',
      email: 'admin@example.com',
      name: 'Admin User',
      role: 'admin',
      team_id: '1',
      created_at: new Date().toISOString(),
    },
    tags: ['incident', 'response', 'critical'],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
  {
    id: '3',
    title: 'Deploying to Production',
    description: 'Step-by-step guide for deploying to production environment',
    category: 'Deployment',
    content: `# Deploying to Production

## Pre-Deployment Checklist
- [ ] All tests passing in CI/CD
- [ ] Code reviewed and approved
- [ ] Release notes prepared
- [ ] Deployment plan communicated to team
- [ ] Monitoring alerts configured
- [ ] Rollback plan documented

## Deployment Steps
1. Create release in Release Manager
2. Review deployment plan
3. Wait for approval from release manager
4. System automatically promotes through:
   - Development → Testing
   - Testing → Staging
   - Staging → Production (with approval)
5. Monitor metrics post-deployment
6. Verify all health checks passing

## Post-Deployment
- Monitor error rates and performance
- Check user reports
- Update deployment log
- Close related issues
- Celebrate successful deployment!`,
    author_id: '1',
    author: {
      id: '1',
      email: 'admin@example.com',
      name: 'Admin User',
      role: 'admin',
      team_id: '1',
      created_at: new Date().toISOString(),
    },
    tags: ['deployment', 'production', 'process'],
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString(),
  },
]

export default function Runbooks() {
  const [runbooks] = useState<Runbook[]>(mockRunbooks)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null)

  const categories = Array.from(
    new Set(runbooks.map((r) => r.category))
  ).sort()

  const filteredRunbooks = runbooks.filter((runbook) => {
    const matchesSearch =
      runbook.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      runbook.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      runbook.tags.some((tag) =>
        tag.toLowerCase().includes(searchQuery.toLowerCase())
      )

    const matchesCategory =
      !selectedCategory || runbook.category === selectedCategory

    return matchesSearch && matchesCategory
  })

  const selectedRunbook = runbooks.find((r) => r.id === selectedId)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-100">Runbooks</h1>
          <p className="text-gray-400 mt-1">
            Operational procedures and troubleshooting guides
          </p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          New Runbook
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left sidebar */}
        <div className="lg:col-span-1 space-y-4">
          {/* Search */}
          <div className="card p-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input
                type="text"
                placeholder="Search runbooks..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="input-field pl-10 w-full text-sm"
              />
            </div>
          </div>

          {/* Categories */}
          <div className="card p-4">
            <h3 className="font-semibold text-gray-100 mb-3">Categories</h3>
            <div className="space-y-2">
              <button
                onClick={() => setSelectedCategory(null)}
                className={`block w-full text-left px-3 py-2 rounded-lg text-sm transition-smooth ${
                  selectedCategory === null
                    ? 'bg-indigo-600 text-white'
                    : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                }`}
              >
                All Categories
              </button>
              {categories.map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`block w-full text-left px-3 py-2 rounded-lg text-sm transition-smooth ${
                    selectedCategory === category
                      ? 'bg-indigo-600 text-white'
                      : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
                  }`}
                >
                  {category}
                </button>
              ))}
            </div>
          </div>

          {/* Runbook list */}
          <div className="card overflow-hidden">
            {filteredRunbooks.length > 0 ? (
              <div className="divide-y divide-gray-700">
                {filteredRunbooks.map((runbook) => (
                  <button
                    key={runbook.id}
                    onClick={() => setSelectedId(runbook.id)}
                    className={`w-full text-left p-4 transition-smooth hover:bg-gray-700/50 ${
                      selectedId === runbook.id ? 'bg-gray-700' : ''
                    }`}
                  >
                    <h4 className="font-medium text-gray-100 text-sm line-clamp-2">
                      {runbook.title}
                    </h4>
                    <p className="text-xs text-gray-500 mt-1">
                      {runbook.category}
                    </p>
                  </button>
                ))}
              </div>
            ) : (
              <div className="p-4 text-center">
                <p className="text-gray-400 text-sm">No runbooks found</p>
              </div>
            )}
          </div>
        </div>

        {/* Right content */}
        <div className="lg:col-span-2">
          {selectedRunbook ? (
            <div className="card p-8">
              {/* Header */}
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-gray-100 mb-2">
                  {selectedRunbook.title}
                </h2>
                <p className="text-gray-400 mb-4">
                  {selectedRunbook.description}
                </p>

                {/* Metadata */}
                <div className="flex flex-wrap gap-4 text-sm text-gray-400 py-4 border-t border-b border-gray-700">
                  <div className="flex items-center gap-2">
                    <User className="w-4 h-4" />
                    <span>{selectedRunbook.author.name}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Calendar className="w-4 h-4" />
                    <span>
                      {new Date(
                        selectedRunbook.updated_at
                      ).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>

              {/* Content */}
              <div className="prose prose-invert max-w-none mb-6 text-gray-300">
                <div
                  className="text-sm leading-relaxed space-y-4"
                  dangerouslySetInnerHTML={{
                    __html: selectedRunbook.content
                      .split('\n')
                      .map((line) => {
                        if (line.startsWith('#')) {
                          const level = line.match(/^#+/)?.[0].length || 1
                          const text = line.replace(/^#+\s/, '')
                          const sizes = {
                            1: 'text-2xl font-bold mt-4 mb-2',
                            2: 'text-xl font-bold mt-3 mb-2',
                            3: 'text-lg font-semibold mt-2 mb-1',
                          }
                          return `<p class="${sizes[level as keyof typeof sizes]}">${text}</p>`
                        }
                        if (line.startsWith('- ')) {
                          return `<li class="ml-4">${line.replace(/^- /, '')}</li>`
                        }
                        if (line.startsWith('```')) {
                          return '<pre class="bg-gray-950 p-3 rounded-lg overflow-x-auto"><code>'
                        }
                        if (line === '```') {
                          return '</code></pre>'
                        }
                        return `<p>${line || '<br />'}</p>`
                      })
                      .join(''),
                  }}
                />
              </div>

              {/* Tags */}
              {selectedRunbook.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 pt-6 border-t border-gray-700">
                  {selectedRunbook.tags.map((tag) => (
                    <span
                      key={tag}
                      className="inline-flex items-center gap-1 px-2 py-1 rounded-full bg-indigo-900/30 text-indigo-300 text-xs"
                    >
                      <Tag className="w-3 h-3" />
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <EmptyState
              title="No runbook selected"
              description="Select a runbook from the list to view its content"
            />
          )}
        </div>
      </div>
    </div>
  )
}
