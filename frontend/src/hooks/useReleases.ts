import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import * as releasesApi from '@/api/releases'
import { Release, PaginatedResponse } from '@/types'

export function useReleases(
  page = 1,
  pageSize = 20,
  filters?: {
    status?: string
    service_id?: string
    search?: string
  }
) {
  return useQuery<PaginatedResponse<Release>>({
    queryKey: ['releases', page, pageSize, filters],
    queryFn: () => releasesApi.getReleases(page, pageSize, filters),
    staleTime: 30 * 1000,
  })
}

export function useRelease(id: string) {
  return useQuery<Release>({
    queryKey: ['release', id],
    queryFn: () => releasesApi.getRelease(id),
    staleTime: 30 * 1000,
  })
}

export function useCreateRelease() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: releasesApi.createRelease,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['releases'] })
    },
  })
}

export function useDeployRelease() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({ releaseId, environment }: { releaseId: string; environment: string }) =>
      releasesApi.deployRelease(releaseId, environment),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['releases'] })
      queryClient.invalidateQueries({ queryKey: ['deployments'] })
    },
  })
}

export function useReleaseHistory(page = 1, pageSize = 50) {
  return useQuery<PaginatedResponse<Release>>({
    queryKey: ['releases-history', page, pageSize],
    queryFn: () => releasesApi.getReleaseHistory(page, pageSize),
    staleTime: 60 * 1000,
  })
}
