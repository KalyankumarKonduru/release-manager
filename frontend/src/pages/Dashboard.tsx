import React from 'react'
import { useMetricsSummary, useDeploymentTrends } from '@/hooks/useAnalytics'
import { useDeployments } from '@/hooks/useDeployments'
import { MetricCard } from '@/components/MetricCard'
import { DeploymentTimeline } from '@/components/DeploymentTimeline'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import { EmptyState } from '@/components/EmptyState'
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
} from 'recharts'
import { Zap, TrendingUp, AlertCircle, Clock } from 'lucide-react'

export default function Dashboard() {
  const { data: metrics, isLoading: metricsLoading } = useMetricsSummary()
  const { data: trends, isLoading: trendsLoading } = useDeploymentTrends(30)
  const { data: deployments, isLoading: deploymentsLoading } = useDeployments(1, 5, {
    status: 'success',
  })

  const isLoading = metricsLoading || trendsLoading || deploymentsLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner text="Loading dashboard..." />
      </div>
    )
  }

  const successRate = metrics
    ? Math.round(metrics.success_rate * 100)
    : 0

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Dashboard</h1>
        <p className="text-gray-400 mt-1">
          Overview of your release pipeline and deployment metrics
        </p>
      </div>

      {/* Metric cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          label="Total Releases"
          value={metrics?.total_releases || 0}
          color="indigo"
          icon={<Zap className="w-8 h-8 text-indigo-400" />}
        />
        <MetricCard
          label="Active Deployments"
          value={metrics?.total_deployments || 0}
          color="blue"
          icon={<TrendingUp className="w-8 h-8 text-blue-400" />}
        />
        <MetricCard
          label="Success Rate"
          value={`${successRate}%`}
          color="green"
          icon={<AlertCircle className="w-8 h-8 text-green-400" />}
        />
        <MetricCard
          label="Avg MTTR"
          value={`${metrics?.average_mttr_hours.toFixed(1) || 0}h`}
          color="purple"
          icon={<Clock className="w-8 h-8 text-purple-400" />}
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Deployment trends */}
        <div className="lg:col-span-2 card p-6">
          <h2 className="text-lg font-semibold text-gray-100 mb-4">
            Deployment Trends (30 Days)
          </h2>
          {trends && trends.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trends}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis
                  dataKey="timestamp"
                  stroke="#9CA3AF"
                  style={{ fontSize: '12px' }}
                  tickFormatter={(value) =>
                    new Date(value).toLocaleDateString('en-US', {
                      month: 'short',
                      day: 'numeric',
                    })
                  }
                />
                <YAxis stroke="#9CA3AF" style={{ fontSize: '12px' }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#111827',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                  }}
                  labelStyle={{ color: '#E5E7EB' }}
                />
                <Line
                  type="monotone"
                  dataKey="deployment_frequency"
                  stroke="#4f46e5"
                  dot={false}
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-80 flex items-center justify-center text-gray-400">
              No data available
            </div>
          )}
        </div>

        {/* Key metrics */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-100 mb-4">
            Key Metrics
          </h2>
          <div className="space-y-4">
            <div>
              <p className="text-xs text-gray-400 font-medium">Deployment Frequency</p>
              <p className="text-2xl font-bold text-indigo-400 mt-1">
                {metrics?.deployment_frequency_per_day.toFixed(2) || 0}/day
              </p>
            </div>
            <div className="border-t border-gray-700 pt-4">
              <p className="text-xs text-gray-400 font-medium">Change Failure Rate</p>
              <p className="text-2xl font-bold text-orange-400 mt-1">
                {(metrics?.change_failure_rate || 0).toFixed(1)}%
              </p>
            </div>
            <div className="border-t border-gray-700 pt-4">
              <p className="text-xs text-gray-400 font-medium">Lead Time</p>
              <p className="text-2xl font-bold text-blue-400 mt-1">
                {metrics?.lead_time_hours.toFixed(1) || 0}h
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent deployments */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-100 mb-4">
          Recent Deployments
        </h2>
        {deployments?.data && deployments.data.length > 0 ? (
          <DeploymentTimeline deployments={deployments.data} />
        ) : (
          <EmptyState
            title="No deployments yet"
            description="Create your first release to get started with deployments"
          />
        )}
      </div>
    </div>
  )
}
