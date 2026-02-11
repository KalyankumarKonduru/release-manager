import { useQuery } from '@tanstack/react-query'
import * as analyticsApi from '@/api/analytics'
import { MetricsSummary, DeploymentMetric, AuditLog } from '@/types'

export function useMetricsSummary() {
  return useQuery<MetricsSummary>({
    queryKey: ['metrics-summary'],
    queryFn: analyticsApi.getMetricsSummary,
    staleTime: 60 * 1000,
  })
}

export function useDeploymentTrends(days = 30) {
  return useQuery<DeploymentMetric[]>({
    queryKey: ['deployment-trends', days],
    queryFn: () => analyticsApi.getDeploymentTrends(days),
    staleTime: 60 * 1000,
  })
}

export function useMetricsByService(service_id?: string) {
  return useQuery<DeploymentMetric[]>({
    queryKey: ['metrics-by-service', service_id],
    queryFn: () => analyticsApi.getMetricsByService(service_id),
    staleTime: 60 * 1000,
  })
}

export function useMetricsByEnvironment(environment?: string) {
  return useQuery<DeploymentMetric[]>({
    queryKey: ['metrics-by-environment', environment],
    queryFn: () => analyticsApi.getMetricsByEnvironment(environment),
    staleTime: 60 * 1000,
  })
}

export function useAuditLogs(
  page = 1,
  pageSize = 50,
  filters?: {
    action?: string
    user_id?: string
    resource_type?: string
    date_from?: string
    date_to?: string
  }
) {
  return useQuery<any>({
    queryKey: ['audit-logs', page, pageSize, filters],
    queryFn: () => analyticsApi.getAuditLogs(page, pageSize, filters),
    staleTime: 30 * 1000,
  })
}
