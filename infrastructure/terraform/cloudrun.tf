# Cloud Run Backend Service
resource "google_cloud_run_service" "backend" {
  name     = "${var.app_name}-backend-${var.environment}"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.backend.email
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}/backend:latest"

        ports {
          container_port = 8000
        }

        env {
          name  = "ENVIRONMENT"
          value = var.environment
        }

        env {
          name  = "DATABASE_URL"
          value = "postgresql://${google_sql_user.main.name}@${google_sql_database_instance.postgres.private_ip_address}:5432/${google_sql_database.main.name}?sslmode=require"
        }

        env {
          name = "POSTGRES_PASSWORD"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.db_password.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name  = "REDIS_URL"
          value = "redis://:${random_password.redis_password.result}@${google_redis_instance.cache.host}:${google_redis_instance.cache.port}/0"
        }

        env {
          name = "JWT_SECRET_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.jwt_secret.secret_id
              key  = "latest"
            }
          }
        }

        env {
          name  = "LOG_LEVEL"
          value = var.environment == "prod" ? "INFO" : "DEBUG"
        }

        env {
          name  = "CORS_ORIGINS"
          value = var.environment == "prod" ? "https://frontend-xxxxxxx.run.app,https://yourdomain.com" : "http://localhost:3000"
        }

        resources {
          limits = {
            cpu    = var.backend_cpu
            memory = var.backend_memory
          }
        }

        startup_probe {
          http_get {
            path = "/health"
            port = 8000
          }
          failure_threshold = 3
          initial_delay_seconds = 10
          timeout_seconds = 5
          period_seconds = 10
        }

        liveness_probe {
          http_get {
            path = "/health"
            port = 8000
          }
          failure_threshold = 3
          initial_delay_seconds = 30
          timeout_seconds = 5
          period_seconds = 30
        }
      }

      timeout_seconds = 3600

      vpc_access_connector {
        name = google_vpc_access_connector.serverless.id
      }
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = var.backend_min_instances
        "autoscaling.knative.dev/maxScale" = var.backend_max_instances
        "run.googleapis.com/cloudsql-instances" = google_sql_database_instance.postgres.connection_name
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [
    google_artifact_registry_repository.docker,
    google_secret_manager_secret_version.db_password,
    google_secret_manager_secret_version.jwt_secret
  ]

  labels = var.labels
}

# Cloud Run Frontend Service
resource "google_cloud_run_service" "frontend" {
  name     = "${var.app_name}-frontend-${var.environment}"
  location = var.region

  template {
    spec {
      service_account_name = google_service_account.frontend.email
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker.repository_id}/frontend:latest"

        ports {
          container_port = 80
        }

        env {
          name  = "VITE_API_BASE_URL"
          value = var.environment == "prod" ? google_cloud_run_service.backend.status[0].url : "http://localhost:8000"
        }

        env {
          name  = "NODE_ENV"
          value = var.environment
        }

        resources {
          limits = {
            cpu    = "1"
            memory = "256Mi"
          }
        }

        startup_probe {
          http_get {
            path = "/health"
            port = 80
          }
          failure_threshold = 3
          initial_delay_seconds = 10
          timeout_seconds = 5
          period_seconds = 10
        }

        liveness_probe {
          http_get {
            path = "/"
            port = 80
          }
          failure_threshold = 3
          initial_delay_seconds = 30
          timeout_seconds = 5
          period_seconds = 30
        }
      }

      timeout_seconds = 300
    }

    metadata {
      annotations = {
        "autoscaling.knative.dev/minScale" = var.frontend_min_instances
        "autoscaling.knative.dev/maxScale" = var.frontend_max_instances
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }

  depends_on = [google_artifact_registry_repository.docker]

  labels = var.labels
}

# Allow public access to backend
resource "google_cloud_run_iam_member" "backend_public" {
  service  = google_cloud_run_service.backend.name
  location = google_cloud_run_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Allow public access to frontend
resource "google_cloud_run_iam_member" "frontend_public" {
  service  = google_cloud_run_service.frontend.name
  location = google_cloud_run_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Cloud Run Domain Mappings for Production
resource "google_cloud_run_domain_mapping" "backend" {
  count    = var.environment == "prod" ? 1 : 0
  name     = "api.yourdomain.com"
  location = var.region
  service_name = google_cloud_run_service.backend.name

  metadata {
    namespace = var.project_id
  }

  depends_on = [google_cloud_run_service.backend]
}

resource "google_cloud_run_domain_mapping" "frontend" {
  count    = var.environment == "prod" ? 1 : 0
  name     = "yourdomain.com"
  location = var.region
  service_name = google_cloud_run_service.frontend.name

  metadata {
    namespace = var.project_id
  }

  depends_on = [google_cloud_run_service.frontend]
}
