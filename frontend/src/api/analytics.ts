import client from './client'
import { MetricsSummary, DeploymentMetric } from '@/types'

export async function getMetricsSummary(): Promise<MetricsSummary> {
  const response = await client.get('/analytics/metrics/summary')
  return response.data
}

export async function getDeploymentTrends(days = 30): Promise<DeploymentMetric[]> {
  const response = await client.get('/analytics/metrics/trends', {
    params: { days },
  })
  return response.data
}

export async function getMetricsByService(service_id?: string): Promise<DeploymentMetric[]> {
  const params = service_id ? { service_id } : {}
  const response = await client.get('/analytics/metrics/by-service', { params })
  return response.data
}

export async function getMetricsByEnvironment(environment?: string): Promise<DeploymentMetric[]> {
  const params = environment ? { environment } : {}
  const response = await client.get('/analytics/metrics/by-environment', { params })
  return response.data
}

export async function getAuditLogs(
  page = 1,
  pageSize = 50,
  filters?: {
    action?: string
    user_id?: string
    resource_type?: string
    date_from?: string
    date_to?: string
  }
): Promise<any> {
  const params = {
    page,
    page_size: pageSize,
    ...filters,
  }
  const response = await client.get('/audit-logs', { params })
  return response.data
}
