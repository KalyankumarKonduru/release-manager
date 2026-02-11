# Service Account for Backend
resource "google_service_account" "backend" {
  account_id   = "${var.app_name}-backend-${var.environment}"
  display_name = "${var.app_name} Backend Service Account"
  description  = "Service account for ${var.app_name} backend Cloud Run service"
}

# Service Account for Frontend
resource "google_service_account" "frontend" {
  account_id   = "${var.app_name}-frontend-${var.environment}"
  display_name = "${var.app_name} Frontend Service Account"
  description  = "Service account for ${var.app_name} frontend Cloud Run service"
}

# Service Account for CI/CD
resource "google_service_account" "cicd" {
  account_id   = "${var.app_name}-cicd-${var.environment}"
  display_name = "${var.app_name} CI/CD Service Account"
  description  = "Service account for ${var.app_name} CI/CD pipelines"
}

# Backend IAM Roles
resource "google_project_iam_member" "backend_cloud_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

resource "google_project_iam_member" "backend_cloud_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

resource "google_project_iam_member" "backend_cloud_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

resource "google_project_iam_member" "backend_cloud_monitoring_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

resource "google_project_iam_member" "backend_artifact_registry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.backend.email}"
}

# Frontend IAM Roles
resource "google_project_iam_member" "frontend_cloud_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.frontend.email}"
}

resource "google_project_iam_member" "frontend_artifact_registry_reader" {
  project = var.project_id
  role    = "roles/artifactregistry.reader"
  member  = "serviceAccount:${google_service_account.frontend.email}"
}

# CI/CD IAM Roles
resource "google_project_iam_member" "cicd_artifact_registry_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.cicd.email}"
}

resource "google_project_iam_member" "cicd_cloud_run_developer" {
  project = var.project_id
  role    = "roles/run.developer"
  member  = "serviceAccount:${google_service_account.cicd.email}"
}

resource "google_project_iam_member" "cicd_cloud_sql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.cicd.email}"
}

resource "google_project_iam_member" "cicd_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cicd.email}"
}

resource "google_project_iam_member" "cicd_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.cicd.email}"
}

resource "google_project_iam_member" "cicd_logging" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.cicd.email}"
}

# Create a service account key for CI/CD authentication
resource "google_service_account_key" "cicd" {
  service_account_id = google_service_account.cicd.name
  public_key_type    = "TYPE_X509_PEM_FILE"
}

# Output service account emails
output "service_account_emails" {
  description = "Service account emails"
  value = {
    backend = google_service_account.backend.email
    frontend = google_service_account.frontend.email
    cicd = google_service_account.cicd.email
  }
}
