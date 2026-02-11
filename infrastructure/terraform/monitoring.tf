# Notification Channel for email alerts
resource "google_monitoring_notification_channel" "email" {
  count           = var.enable_monitoring ? 1 : 0
  display_name    = "${var.app_name} Email Notifications"
  type            = "email"
  labels          = { email_address = var.alert_email }
  enabled         = true
  force_delete    = false
}

# Backend Service Uptime Check
resource "google_monitoring_uptime_check_config" "backend" {
  count           = var.enable_monitoring ? 1 : 0
  display_name    = "${var.app_name} Backend Uptime"
  timeout         = "10s"
  period          = "60s"
  selected_regions = ["USA", "EUROPE", "ASIA_PACIFIC"]

  http_check {
    path = "/health"
    port = 443
    use_ssl = true
    accepted_response_status_codes {
      status_values = ["200"]
    }
  }

  monitored_resource {
    type = "uptime-url"
    labels = {
      host = trimsuffix(google_cloud_run_service.backend.status[0].url, "/")
    }
  }
}

# Alert Policy: Backend Error Rate
resource "google_monitoring_alert_policy" "backend_error_rate" {
  count           = var.enable_monitoring ? 1 : 0
  display_name    = "${var.app_name} Backend Error Rate"
  combiner        = "OR"
  enabled         = true

  conditions {
    display_name = "Error rate > 5%"
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"${google_cloud_run_service.backend.name}\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class=\"5xx\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.05
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_RATE"
      }
    }
  }

  notification_channels = var.enable_monitoring ? [google_monitoring_notification_channel.email[0].id] : []
  documentation {
    content = "Backend error rate exceeded 5%. Check Cloud Run logs for details."
  }
}

# Alert Policy: Backend High Latency
resource "google_monitoring_alert_policy" "backend_latency" {
  count           = var.enable_monitoring ? 1 : 0
  display_name    = "${var.app_name} Backend High Latency"
  combiner        = "OR"
  enabled         = true

  conditions {
    display_name = "P95 Latency > 2s"
    condition_threshold {
      filter          = "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"${google_cloud_run_service.backend.name}\" AND metric.type=\"run.googleapis.com/request_latencies\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 2000
      aggregations {
        alignment_period       = "60s"
        per_series_aligner     = "ALIGN_PERCENTILE_95"
        cross_series_reducer   = "REDUCE_PERCENTILE_95"
      }
    }
  }

  notification_channels = var.enable_monitoring ? [google_monitoring_notification_channel.email[0].id] : []
  documentation {
    content = "Backend latency is high. Check Cloud Run metrics and database performance."
  }
}

# Alert Policy: Cloud SQL CPU
resource "google_monitoring_alert_policy" "cloudsql_cpu" {
  count           = var.enable_monitoring ? 1 : 0
  display_name    = "${var.app_name} Cloud SQL High CPU"
  combiner        = "OR"
  enabled         = true

  conditions {
    display_name = "CPU > 80%"
    condition_threshold {
      filter          = "resource.type=\"cloudsql_database\" AND resource.label.database_id=\"${var.project_id}:${google_sql_database_instance.postgres.name}\" AND metric.type=\"cloudsql.googleapis.com/database/cpu/utilization\""
      duration        = "600s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.8
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = var.enable_monitoring ? [google_monitoring_notification_channel.email[0].id] : []
  documentation {
    content = "Cloud SQL CPU utilization is high. Consider upgrading the instance tier."
  }
}

# Alert Policy: Cloud SQL Disk
resource "google_monitoring_alert_policy" "cloudsql_disk" {
  count           = var.enable_monitoring ? 1 : 0
  display_name    = "${var.app_name} Cloud SQL High Disk Usage"
  combiner        = "OR"
  enabled         = true

  conditions {
    display_name = "Disk > 85%"
    condition_threshold {
      filter          = "resource.type=\"cloudsql_database\" AND resource.label.database_id=\"${var.project_id}:${google_sql_database_instance.postgres.name}\" AND metric.type=\"cloudsql.googleapis.com/database/disk/utilization\""
      duration        = "600s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.85
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = var.enable_monitoring ? [google_monitoring_notification_channel.email[0].id] : []
  documentation {
    content = "Cloud SQL disk usage is high. Consider increasing storage allocation."
  }
}

# Alert Policy: Redis Memory
resource "google_monitoring_alert_policy" "redis_memory" {
  count           = var.enable_monitoring ? 1 : 0
  display_name    = "${var.app_name} Redis High Memory Usage"
  combiner        = "OR"
  enabled         = true

  conditions {
    display_name = "Memory > 90%"
    condition_threshold {
      filter          = "resource.type=\"redis_instance\" AND resource.label.instance_id=\"${google_redis_instance.cache.name}\" AND metric.type=\"redis.googleapis.com/stats/memory/usage_ratio\""
      duration        = "300s"
      comparison      = "COMPARISON_GT"
      threshold_value = 0.9
      aggregations {
        alignment_period   = "60s"
        per_series_aligner = "ALIGN_MEAN"
      }
    }
  }

  notification_channels = var.enable_monitoring ? [google_monitoring_notification_channel.email[0].id] : []
  documentation {
    content = "Redis memory usage is high. Consider increasing memory size or optimizing cache keys."
  }
}

# Dashboard for monitoring
resource "google_monitoring_dashboard" "main" {
  count          = var.enable_monitoring ? 1 : 0
  dashboard_json = jsonencode({
    displayName = "${var.app_name} Dashboard"
    mosaicLayout = {
      columns = 12
      tiles = [
        {
          width  = 6
          height = 4
          widget = {
            title = "Backend Request Rate"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"${google_cloud_run_service.backend.name}\" AND metric.type=\"run.googleapis.com/request_count\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_RATE"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          xPos   = 6
          width  = 6
          height = 4
          widget = {
            title = "Backend Error Rate"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloud_run_revision\" AND resource.label.service_name=\"${google_cloud_run_service.backend.name}\" AND metric.type=\"run.googleapis.com/request_count\" AND metric.label.response_code_class=\"5xx\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_RATE"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          yPos   = 4
          width  = 6
          height = 4
          widget = {
            title = "Cloud SQL CPU"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"cloudsql_database\" AND resource.label.database_id=\"${var.project_id}:${google_sql_database_instance.postgres.name}\" AND metric.type=\"cloudsql.googleapis.com/database/cpu/utilization\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_MEAN"
                      }
                    }
                  }
                }
              ]
            }
          }
        },
        {
          xPos   = 6
          yPos   = 4
          width  = 6
          height = 4
          widget = {
            title = "Redis Memory Usage"
            xyChart = {
              dataSets = [
                {
                  timeSeriesQuery = {
                    timeSeriesFilter = {
                      filter = "resource.type=\"redis_instance\" AND resource.label.instance_id=\"${google_redis_instance.cache.name}\" AND metric.type=\"redis.googleapis.com/stats/memory/usage_ratio\""
                      aggregation = {
                        alignmentPeriod  = "60s"
                        perSeriesAligner = "ALIGN_MEAN"
                      }
                    }
                  }
                }
              ]
            }
          }
        }
      ]
    }
  })

  depends_on = [
    google_cloud_run_service.backend,
    google_sql_database_instance.postgres,
    google_redis_instance.cache
  ]
}
