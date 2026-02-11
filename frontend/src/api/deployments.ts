import client from './client'
import { Deployment, PaginatedResponse, PipelineStage } from '@/types'

interface ApproveDeploymentPayload {
  comment?: string
}

interface RollbackPayload {
  reason: string
}

export async function getDeployments(
  page = 1,
  pageSize = 20,
  filters?: {
    status?: string
    environment?: string
    service_id?: string
  }
): Promise<PaginatedResponse<Deployment>> {
  const params = {
    page,
    page_size: pageSize,
    ...filters,
  }
  const response = await client.get('/deployments', { params })
  return response.data
}

export async function getDeployment(id: string): Promise<Deployment> {
  const response = await client.get(`/deployments/${id}`)
  return response.data
}

export async function approveDeployment(
  deploymentId: string,
  payload: ApproveDeploymentPayload
): Promise<Deployment> {
  const response = await client.post(`/deployments/${deploymentId}/approve`, payload)
  return response.data
}

export async function rejectDeployment(
  deploymentId: string,
  comment?: string
): Promise<Deployment> {
  const response = await client.post(`/deployments/${deploymentId}/reject`, { comment })
  return response.data
}

export async function rollbackDeployment(
  deploymentId: string,
  payload: RollbackPayload
): Promise<Deployment> {
  const response = await client.post(`/deployments/${deploymentId}/rollback`, payload)
  return response.data
}

export async function getDeploymentStages(deploymentId: string): Promise<PipelineStage[]> {
  const response = await client.get(`/deployments/${deploymentId}/stages`)
  return response.data
}

export async function getDeploymentLogs(deploymentId: string, stageId?: string): Promise<string> {
  const params = stageId ? { stage_id: stageId } : {}
  const response = await client.get(`/deployments/${deploymentId}/logs`, { params })
  return response.data
}
