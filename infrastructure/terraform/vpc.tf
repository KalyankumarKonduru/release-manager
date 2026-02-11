# VPC Network
resource "google_compute_network" "main" {
  name                    = "${var.app_name}-vpc-${var.environment}"
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"

  depends_on = [null_resource.api_wait]

  labels = var.labels
}

# Primary subnet for GKE (if needed in future)
resource "google_compute_subnetwork" "private" {
  name          = "${var.app_name}-private-subnet-${var.environment}"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.region
  network       = google_compute_network.main.id
  private_ip_google_access = true

  labels = var.labels

  log_config {
    aggregation_interval = "INTERVAL_5_SEC"
    flow_logs_enabled    = true
    metadata             = "INCLUDE_ALL_METADATA"
  }
}

# Cloud NAT for private subnet egress
resource "google_compute_router" "main" {
  name    = "${var.app_name}-router-${var.environment}"
  region  = var.region
  network = google_compute_network.main.id

  labels = var.labels
}

resource "google_compute_router_nat" "main" {
  name                               = "${var.app_name}-nat-${var.environment}"
  router                             = google_compute_router.main.name
  region                             = google_compute_router.main.region
  nat_ip_allocate_option             = "AUTO_ONLY"
  source_subnetwork_ip_ranges_to_nat = "ALL_SUBNETWORKS_ALL_IP_RANGES"
  enable_dynamic_port_allocation     = true
  enable_endpoint_independent_mapping = false

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# Serverless VPC Connector for Cloud Run to access private resources
resource "google_vpc_access_connector" "serverless" {
  name          = "${var.app_name}-serverless-connector-${var.environment}"
  region        = var.region
  ip_cidr_range = "10.8.0.0/28"
  network       = google_compute_network.main.name
  min_throughput = 200
  max_throughput = 1000

  depends_on = [google_compute_network.main]
}

# Service Networking Connection for managed services (Cloud SQL, Memorystore)
resource "google_service_networking_connection" "private_vpc_connection" {
  network            = google_compute_network.main.id
  service            = "servicenetworking.googleapis.com"
  reserved_peering_ranges = [google_compute_global_address.private_ip_address.name]

  depends_on = [google_compute_network.main]
}

resource "google_compute_global_address" "private_ip_address" {
  name          = "${var.app_name}-private-ip-${var.environment}"
  purpose       = "VPC_PEERING"
  address_type  = "INTERNAL"
  prefix_length = 16
  network       = google_compute_network.main.id
}

# Firewall rules
resource "google_compute_firewall" "allow_internal" {
  name    = "${var.app_name}-allow-internal-${var.environment}"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
  }

  allow {
    protocol = "udp"
  }

  source_ranges = ["10.0.0.0/8"]
  target_tags   = ["internal"]

  labels = var.labels
}

resource "google_compute_firewall" "allow_health_checks" {
  name    = "${var.app_name}-allow-health-checks-${var.environment}"
  network = google_compute_network.main.name

  allow {
    protocol = "tcp"
  }

  source_ranges = ["35.191.0.0/16", "130.211.0.0/22"]
  target_tags   = ["allow-health-checks"]

  labels = var.labels
}
