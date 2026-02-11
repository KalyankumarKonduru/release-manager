import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as deploymentsApi from '@/api/deployments'
import { Deployment, PaginatedResponse } from '@/types'

export function useDeployments(
  page = 1,
  pageSize = 20,
  filters?: {
    status?: string
    environment?: string
    service_id?: string
  }
) {
  return useQuery<PaginatedResponse<Deployment>>({
    queryKey: ['deployments', page, pageSize, filters],
    queryFn: () => deploymentsApi.getDeployments(page, pageSize, filters),
    staleTime: 30 * 1000,
  })
}

export function useDeployment(id: string) {
  return useQuery<Deployment>({
    queryKey: ['deployment', id],
    queryFn: () => deploymentsApi.getDeployment(id),
    staleTime: 30 * 1000,
  })
}

export function useApproveDeployment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ deploymentId, comment }: { deploymentId: string; comment?: string }) =>
      deploymentsApi.approveDeployment(deploymentId, { comment }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deployments'] })
    },
  })
}

export function useRejectDeployment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ deploymentId, comment }: { deploymentId: string; comment?: string }) =>
      deploymentsApi.rejectDeployment(deploymentId, comment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deployments'] })
    },
  })
}

export function useRollbackDeployment() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ deploymentId, reason }: { deploymentId: string; reason: string }) =>
      deploymentsApi.rollbackDeployment(deploymentId, { reason }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['deployments'] })
    },
  })
}

export function useDeploymentStages(deploymentId: string) {
  return useQuery({
    queryKey: ['deployment-stages', deploymentId],
    queryFn: () => deploymentsApi.getDeploymentStages(deploymentId),
    staleTime: 10 * 1000,
  })
}

export function useDeploymentLogs(deploymentId: string, stageId?: string) {
  return useQuery({
    queryKey: ['deployment-logs', deploymentId, stageId],
    queryFn: () => deploymentsApi.getDeploymentLogs(deploymentId, stageId),
    staleTime: 5 * 1000,
  })
}
