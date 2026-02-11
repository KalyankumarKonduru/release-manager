output "cloud_run_backend_url" {
  description = "URL of the backend Cloud Run service"
  value       = google_cloud_run_service.backend.status[0].url
}

output "cloud_run_frontend_url" {
  description = "URL of the frontend Cloud Run service"
  value       = google_cloud_run_service.frontend.status[0].url
}

output "cloud_sql_instance_connection_name" {
  description = "Cloud SQL instance connection name"
  value       = google_sql_database_instance.postgres.connection_name
}

output "cloud_sql_private_ip" {
  description = "Cloud SQL private IP address"
  value       = google_sql_database_instance.postgres.private_ip_address
}

output "cloud_sql_database_name" {
  description = "Cloud SQL database name"
  value       = google_sql_database.main.name
}

output "redis_host" {
  description = "Redis instance host"
  value       = google_redis_instance.cache.host
}

output "redis_port" {
  description = "Redis instance port"
  value       = google_redis_instance.cache.port
}

output "artifact_registry_repository_url" {
  description = "Artifact Registry repository URL"
  value       = google_artifact_registry_repository.docker.repository_config[0].docker_config
}

output "vpc_network_name" {
  description = "VPC network name"
  value       = google_compute_network.main.name
}

output "vpc_network_id" {
  description = "VPC network ID"
  value       = google_compute_network.main.id
}

output "serverless_connector_id" {
  description = "Serverless VPC Connector ID"
  value       = google_vpc_access_connector.serverless.id
}

output "backend_service_account_email" {
  description = "Backend service account email"
  value       = google_service_account.backend.email
}

output "frontend_service_account_email" {
  description = "Frontend service account email"
  value       = google_service_account.frontend.email
}

output "backend_domain" {
  description = "Custom domain for backend (if configured)"
  value       = var.environment == "prod" ? google_cloud_run_domain_mapping.backend[0].name : null
}

output "frontend_domain" {
  description = "Custom domain for frontend (if configured)"
  value       = var.environment == "prod" ? google_cloud_run_domain_mapping.frontend[0].name : null
}

output "database_password_secret_id" {
  description = "Secret Manager secret ID for database password"
  value       = google_secret_manager_secret.db_password.id
}

output "redis_auth_secret_id" {
  description = "Secret Manager secret ID for Redis authentication"
  value       = google_secret_manager_secret.redis_auth.id
}

output "jwt_secret_id" {
  description = "Secret Manager secret ID for JWT secret"
  value       = google_secret_manager_secret.jwt_secret.id
}

output "monitoring_notification_channel_id" {
  description = "Monitoring notification channel ID"
  value       = try(google_monitoring_notification_channel.email[0].id, null)
}

output "terraform_state_bucket" {
  description = "GCS bucket for Terraform state"
  value       = "release-manager-terraform-state"
}

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "environment" {
  description = "Environment name"
  value       = var.environment
}
