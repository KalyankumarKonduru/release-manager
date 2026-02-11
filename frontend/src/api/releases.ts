import client from './client'
import { Release, PaginatedResponse } from '@/types'

interface CreateReleasePayload {
  service_id: string
  version: string
  branch: string
  commit_hash: string
  description?: string
}

export async function getReleases(
  page = 1,
  pageSize = 20,
  filters?: {
    status?: string
    service_id?: string
    search?: string
  }
): Promise<PaginatedResponse<Release>> {
  const params = {
    page,
    page_size: pageSize,
    ...filters,
  }
  const response = await client.get('/releases', { params })
  return response.data
}

export async function getRelease(id: string): Promise<Release> {
  const response = await client.get(`/releases/${id}`)
  return response.data
}

export async function createRelease(payload: CreateReleasePayload): Promise<Release> {
  const response = await client.post('/releases', payload)
  return response.data
}

export async function deployRelease(releaseId: string, environment: string): Promise<Release> {
  const response = await client.post(`/releases/${releaseId}/deploy`, { environment })
  return response.data
}

export async function getReleaseHistory(
  page = 1,
  pageSize = 50
): Promise<PaginatedResponse<Release>> {
  const response = await client.get('/releases/history', {
    params: { page, page_size: pageSize },
  })
  return response.data
}
