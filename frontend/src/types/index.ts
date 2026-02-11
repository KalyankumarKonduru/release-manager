export interface User {
  id: string
  email: string
  name?: string
  full_name?: string
  username?: string
  avatar?: string
  role?: 'admin' | 'release-manager' | 'developer' | 'viewer'
  is_active?: boolean
  is_admin?: boolean
  team_id?: string
  created_at: string
}

export interface Team {
  id: string
  name: string
  description?: string
  created_at: string
  updated_at: string
}

export interface Service {
  id: string
  name: string
  description?: string
  repository_url: string
  team_id: string
  created_at: string
  updated_at: string
}

export type Environment = 'dev' | 'staging' | 'production'

export interface Release {
  id: string
  version: string
  service_id: string
  service: Service
  branch: string
  commit_hash: string
  author: User
  description?: string
  created_at: string
  updated_at: string
  status: 'draft' | 'pending' | 'deployed' | 'failed'
}

export interface PipelineStage {
  id: string
  name: string
  order: number
  environment: Environment
  status: 'pending' | 'running' | 'success' | 'failed'
  started_at?: string
  completed_at?: string
  logs_url?: string
}

export interface Deployment {
  id: string
  release_id: string
  release: Release
  environment: Environment
  status: 'pending' | 'approved' | 'in_progress' | 'success' | 'failed' | 'rolled_back'
  requested_by: User
  approved_by?: User
  approval_comment?: string
  deployed_at?: string
  approved_at?: string
  created_at: string
  pipeline_stages: PipelineStage[]
}

export interface Approval {
  id: string
  deployment_id: string
  deployment: Deployment
  requested_by: User
  status: 'pending' | 'approved' | 'rejected'
  comment?: string
  created_at: string
  updated_at: string
}

export interface Rollback {
  id: string
  deployment_id: string
  previous_deployment_id: string
  initiated_by: User
  reason: string
  status: 'pending' | 'in_progress' | 'success' | 'failed'
  created_at: string
  completed_at?: string
}

export interface AuditLog {
  id: string
  user_id: string
  user: User
  action: string
  resource_type: string
  resource_id: string
  changes?: Record<string, unknown>
  ip_address?: string
  user_agent?: string
  created_at: string
}

export interface Runbook {
  id: string
  title: string
  description: string
  category: string
  content: string
  author_id: string
  author: User
  tags: string[]
  created_at: string
  updated_at: string
}

export interface DeploymentMetric {
  timestamp: string
  deployment_frequency: number
  lead_time_hours: number
  change_failure_rate: number
  mttr_hours: number
  service: string
  environment: Environment
}

export interface MetricsSummary {
  total_releases: number
  total_deployments: number
  success_rate: number
  average_mttr_hours: number
  deployment_frequency_per_day: number
  change_failure_rate: number
  lead_time_hours: number
  last_30_days_metrics: DeploymentMetric[]
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AuthToken {
  access_token: string
  token_type: string
  expires_in: number
}

export interface EnvironmentStatus {
  environment: Environment
  last_deployment?: Deployment
  health: 'healthy' | 'warning' | 'critical'
  uptime_percentage: number
}
