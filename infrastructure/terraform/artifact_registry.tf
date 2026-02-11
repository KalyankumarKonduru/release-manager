# Artifact Registry Repository for Docker images
resource "google_artifact_registry_repository" "docker" {
  location      = var.region
  repository_id = var.artifact_registry_repository
  description   = "Docker repository for ${var.app_name} application"
  format        = "DOCKER"

  docker_config {
    immutable_tags = var.environment == "prod" ? true : false
  }

  depends_on = [null_resource.api_wait]

  labels = var.labels
}

# Grant permissions to Cloud Run service accounts
resource "google_artifact_registry_repository_iam_member" "backend" {
  location   = google_artifact_registry_repository.docker.location
  repository = google_artifact_registry_repository.docker.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.backend.email}"
}

resource "google_artifact_registry_repository_iam_member" "frontend" {
  location   = google_artifact_registry_repository.docker.location
  repository = google_artifact_registry_repository.docker.name
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.frontend.email}"
}

# Output artifact registry URL
output "artifact_registry_url" {
  description = "Artifact Registry repository URL"
  value       = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}"
}
