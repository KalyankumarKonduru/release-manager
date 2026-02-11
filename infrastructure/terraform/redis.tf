# Memorystore Redis Instance
resource "google_redis_instance" "cache" {
  name           = "${var.app_name}-redis-${var.environment}"
  tier           = var.redis_tier
  memory_size_gb = var.redis_memory_size_gb
  region         = var.region
  redis_version  = "7.0"
  display_name   = "${var.app_name} Redis Cache (${var.environment})"

  authorized_network = google_compute_network.main.id
  connect_mode       = "PRIVATE_SERVICE_ACCESS"

  auth_enabled    = true
  auth_string     = random_password.redis_password.result
  transit_encryption_mode = "SERVER_AUTHENTICATION"

  maintenance_policy {
    weekly_maintenance_window {
      day        = "SUNDAY"
      start_time {
        hours   = 3
        minutes = 0
      }
    }
  }

  persistence_config {
    persistence_mode = var.environment == "prod" ? "RDB" : "DISABLED"
  }

  replica_configuration {
    available_zone = data.google_compute_zones.available.names[1]
  }

  depends_on = [
    google_service_networking_connection.private_vpc_connection,
    null_resource.api_wait
  ]

  labels = merge(var.labels, {
    cache = "redis"
  })

  lifecycle {
    prevent_destroy = false
  }
}

# Random password for Redis auth
resource "random_password" "redis_password" {
  length  = 32
  special = true
}

# Store Redis auth in Secret Manager
resource "google_secret_manager_secret" "redis_auth" {
  secret_id = "${var.app_name}-redis-auth-${var.environment}"
  replication {
    automatic = true
  }

  labels = var.labels
}

resource "google_secret_manager_secret_version" "redis_auth" {
  secret      = google_secret_manager_secret.redis_auth.id
  secret_data = "redis://:${random_password.redis_password.result}@${google_redis_instance.cache.host}:${google_redis_instance.cache.port}/0"
}

# Data source for available zones
data "google_compute_zones" "available" {
  project = var.project_id
  region  = var.region
}
