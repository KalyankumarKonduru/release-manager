import React, { useState } from 'react'
import { useMetricsSummary, useDeploymentTrends, useMetricsByService } from '@/hooks/useAnalytics'
import { MetricCard } from '@/components/MetricCard'
import { LoadingSpinner } from '@/components/LoadingSpinner'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts'
import { TrendingUp } from 'lucide-react'

export default function Analytics() {
  const { data: metrics, isLoading: metricsLoading } = useMetricsSummary()
  const { data: trends, isLoading: trendsLoading } = useDeploymentTrends(30)
  const { data: serviceMetrics, isLoading: serviceLoading } = useMetricsByService()

  const isLoading = metricsLoading || trendsLoading || serviceLoading

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <LoadingSpinner text="Loading analytics..." />
      </div>
    )
  }

  const COLORS = ['#4f46e5', '#8b5cf6', '#06b6d4', '#10b981', '#f59e0b']

  // Prepare data for service breakdown
  const serviceData =
    serviceMetrics?.slice(0, 5).map((m, idx) => ({
      name: m.service || 'Unknown',
      frequency: m.deployment_frequency,
      mttr: Math.round(m.mttr_hours),
    })) || []

  // Prepare data for DORA metrics radar
  const doraData = [
    {
      metric: 'Deployment Freq',
      value: Math.min((metrics?.deployment_frequency_per_day || 0) * 10, 100),
    },
    {
      metric: 'Lead Time',
      value: Math.min(100 - (metrics?.lead_time_hours || 0), 100),
    },
    {
      metric: 'Success Rate',
      value: metrics?.success_rate ? (metrics.success_rate * 100) : 0,
    },
    {
      metric: 'MTTR',
      value: Math.min(100 - (metrics?.average_mttr_hours || 0), 100),
    },
  ]

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-100">Analytics & DORA Metrics</h1>
        <p className="text-gray-400 mt-1">
          Deployment frequency, lead time, change failure rate, and mean time to recovery
        </p>
      </div>

      {/* DORA Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          label="Deployment Frequency"
          value={metrics?.deployment_frequency_per_day.toFixed(2) || 0}
          unit="per day"
          trend={5}
          color="indigo"
          icon={<TrendingUp className="w-8 h-8 text-indigo-400" />}
        />
        <MetricCard
          label="Lead Time"
          value={metrics?.lead_time_hours.toFixed(1) || 0}
          unit="hours"
          trend={-3}
          color="blue"
        />
        <MetricCard
          label="Change Failure Rate"
          value={(metrics?.change_failure_rate || 0).toFixed(1)}
          unit="%"
          trend={-2}
          color="purple"
        />
        <MetricCard
          label="MTTR"
          value={metrics?.average_mttr_hours.toFixed(1) || 0}
          unit="hours"
          trend={-8}
          color="green"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Deployment Frequency Trend */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-100 mb-4">
            Deployment Frequency (30 Days)
          </h2>
          {trends && trends.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trends}>
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
                <Bar dataKey="deployment_frequency" fill="#4f46e5" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-80 flex items-center justify-center text-gray-400">
              No data available
            </div>
          )}
        </div>

        {/* Lead Time Distribution */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-100 mb-4">
            Lead Time Distribution
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
                  dataKey="lead_time_hours"
                  stroke="#8b5cf6"
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
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* DORA Metrics Radar */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-100 mb-4">
            DORA Performance
          </h2>
          {doraData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={doraData}>
                <PolarGrid stroke="#374151" />
                <PolarAngleAxis dataKey="metric" stroke="#9CA3AF" />
                <PolarRadiusAxis stroke="#9CA3AF" angle={90} domain={[0, 100]} />
                <Radar
                  name="Performance"
                  dataKey="value"
                  stroke="#4f46e5"
                  fill="#4f46e5"
                  fillOpacity={0.5}
                />
              </RadarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-80 flex items-center justify-center text-gray-400">
              No data available
            </div>
          )}
        </div>

        {/* Service Breakdown */}
        <div className="card p-6">
          <h2 className="text-lg font-semibold text-gray-100 mb-4">
            Deployments by Service
          </h2>
          {serviceData.length > 0 ? (
            <div className="space-y-4">
              {serviceData.map((service, idx) => (
                <div key={idx}>
                  <div className="flex justify-between mb-2">
                    <span className="text-sm text-gray-300">{service.name}</span>
                    <span className="text-sm font-semibold text-gray-100">
                      {service.frequency.toFixed(2)} deploys
                    </span>
                  </div>
                  <div className="w-full h-2 bg-gray-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-indigo-600 to-purple-600"
                      style={{
                        width: `${(service.frequency / 5) * 100}%`,
                      }}
                    />
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="h-80 flex items-center justify-center text-gray-400">
              No service data available
            </div>
          )}
        </div>
      </div>

      {/* MTTR Trend */}
      <div className="card p-6">
        <h2 className="text-lg font-semibold text-gray-100 mb-4">
          Mean Time to Recovery (MTTR)
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
              <Legend />
              <Line
                type="monotone"
                dataKey="mttr_hours"
                stroke="#10b981"
                dot={false}
                strokeWidth={2}
                name="MTTR (hours)"
              />
            </LineChart>
          </ResponsiveContainer>
        ) : (
          <div className="h-80 flex items-center justify-center text-gray-400">
            No data available
          </div>
        )}
      </div>
    </div>
  )
}
