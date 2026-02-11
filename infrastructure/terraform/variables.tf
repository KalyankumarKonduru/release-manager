variable "project_id" {
  description = "GCP Project ID"
  type        = string
  nullable    = false
}

variable "region" {
  description = "GCP Region"
  type        = string
  default     = "us-central1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "app_name" {
  description = "Application name"
  type        = string
  default     = "release-manager"
}

variable "database_tier" {
  description = "Cloud SQL database tier"
  type        = string
  default     = "db-f1-micro"
  validation {
    condition     = contains(["db-f1-micro", "db-g1-small", "db-n1-standard-1", "db-n1-standard-2", "db-n1-standard-4"], var.database_tier)
    error_message = "Database tier must be a valid Cloud SQL tier."
  }
}

variable "redis_memory_size_gb" {
  description = "Redis memory size in GB"
  type        = number
  default     = 1
  validation {
    condition     = var.redis_memory_size_gb >= 1 && var.redis_memory_size_gb <= 300
    error_message = "Redis memory size must be between 1 and 300 GB."
  }
}

variable "redis_tier" {
  description = "Redis tier (basic or standard)"
  type        = string
  default     = "basic"
  validation {
    condition     = contains(["basic", "standard"], var.redis_tier)
    error_message = "Redis tier must be basic or standard."
  }
}

variable "backend_min_instances" {
  description = "Minimum number of Cloud Run instances for backend"
  type        = number
  default     = 1
  validation {
    condition     = var.backend_min_instances >= 0 && var.backend_min_instances <= 100
    error_message = "Minimum instances must be between 0 and 100."
  }
}

variable "backend_max_instances" {
  description = "Maximum number of Cloud Run instances for backend"
  type        = number
  default     = 10
  validation {
    condition     = var.backend_max_instances >= 1 && var.backend_max_instances <= 100
    error_message = "Maximum instances must be between 1 and 100."
  }
}

variable "backend_memory" {
  description = "Memory allocation for backend Cloud Run service (Mi)"
  type        = string
  default     = "512Mi"
}

variable "backend_cpu" {
  description = "CPU allocation for backend Cloud Run service"
  type        = string
  default     = "1"
}

variable "frontend_min_instances" {
  description = "Minimum number of Cloud Run instances for frontend"
  type        = number
  default     = 1
}

variable "frontend_max_instances" {
  description = "Maximum number of Cloud Run instances for frontend"
  type        = number
  default     = 5
}

variable "artifact_registry_repository" {
  description = "Artifact Registry repository name"
  type        = string
  default     = "release-manager"
}

variable "enable_monitoring" {
  description = "Enable Cloud Monitoring and Alerting"
  type        = bool
  default     = true
}

variable "alert_email" {
  description = "Email address for alert notifications"
  type        = string
  nullable    = false
}

variable "database_backup_location" {
  description = "Location for database backups"
  type        = string
  default     = "us"
}

variable "enable_ha_database" {
  description = "Enable High Availability for Cloud SQL"
  type        = bool
  default     = false
}

variable "database_availability_type" {
  description = "Availability type for Cloud SQL (REGIONAL or ZONAL)"
  type        = string
  default     = "ZONAL"
  validation {
    condition     = contains(["REGIONAL", "ZONAL"], var.database_availability_type)
    error_message = "Database availability type must be REGIONAL or ZONAL."
  }
}

variable "labels" {
  description = "Common labels to apply to all resources"
  type        = map(string)
  default = {
    terraform   = "true"
    environment = "dev"
    project     = "release-manager"
  }
}
