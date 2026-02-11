# Cloud SQL PostgreSQL Instance
resource "google_sql_database_instance" "postgres" {
  name             = "${var.app_name}-postgres-${var.environment}"
  database_version = "POSTGRES_15"
  region           = var.region
  deletion_protection = var.environment == "prod"

  settings {
    tier              = var.database_tier
    availability_type = var.database_availability_type
    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      location                       = var.database_backup_location
      point_in_time_recovery_enabled = true
      transaction_log_retention_days = 7
      backup_retention_settings {
        retained_backups = 30
        retention_unit   = "COUNT"
      }
    }

    database_flags {
      name  = "cloudsql_iam_authentication"
      value = "on"
    }

    database_flags {
      name  = "max_connections"
      value = "100"
    }

    database_flags {
      name  = "shared_buffers"
      value = "262144" # 2GB for db-f1-micro
    }

    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    database_flags {
      name  = "log_min_duration_statement"
      value = "1000"
    }

    ip_configuration {
      ipv4_enabled                                  = var.environment != "prod"
      private_network                               = google_compute_network.main.id
      enable_private_path_for_cloudsql_cloud_sql    = true
      require_ssl                                   = true
      authorized_networks {
        name  = "office"
        value = "0.0.0.0/0"
      }
    }

    insights_config {
      query_insights_enabled = true
      query_string_length    = 1024
      record_application_tags = false
    }

    maintenance_window {
      day          = 7 # Sunday
      hour         = 3
      update_track = "stable"
    }
  }

  depends_on = [
    google_service_networking_connection.private_vpc_connection,
    null_resource.api_wait
  ]

  labels = merge(var.labels, {
    database = "postgresql"
  })
}

# PostgreSQL Database
resource "google_sql_database" "main" {
  name     = "${var.app_name}_db"
  instance = google_sql_database_instance.postgres.name
  charset  = "UTF8"
  collation = "en_US.UTF8"

  lifecycle {
    prevent_destroy = false
  }
}

# Database user
resource "google_sql_user" "main" {
  name     = "${var.app_name}_user"
  instance = google_sql_database_instance.postgres.name
  password = random_password.db_password.result
  type     = "BUILT_IN"
}

# Random password for database user
resource "random_password" "db_password" {
  length  = 32
  special = true
}

# Store DB password in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "${var.app_name}-db-password-${var.environment}"
  replication {
    automatic = true
  }

  labels = var.labels
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

# Output database connection string
output "database_connection_string" {
  description = "Database connection string"
  value       = "postgresql://${google_sql_user.main.name}:${random_password.db_password.result}@${google_sql_database_instance.postgres.private_ip_address}:5432/${google_sql_database.main.name}"
  sensitive   = true
}
