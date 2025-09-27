resource "google_container_cluster" "primary" {
  name                     = var.cluster_name
  location                 = var.region
  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = false
  networking_mode          = "VPC_NATIVE"
  network                  = var.vpc_name
  subnetwork               = var.subnet_name
  # node_locations           = ["${var.region}-a"] # single zone to save cost
  node_locations = [
    "${var.region}-a",
    "${var.region}-b"
  ] # multi zone for HA

  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
  }

  ip_allocation_policy {
    cluster_secondary_range_name  = "${var.region}-gke-pods"
    services_secondary_range_name = "${var.region}-gke-services"
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "192.168.0.0/28" # CIDR block for control plane
  }
}

resource "google_container_node_pool" "primary_nodes" {
  name     = "${var.cluster_name}-node-pool"
  cluster  = google_container_cluster.primary.name
  location = var.region

  node_locations = [
    "${var.region}-a",
    "${var.region}-b",
    # "${var.region}-c"
  ]

  initial_node_count = 1

  autoscaling {
    total_max_node_count = 4
    total_min_node_count = 1
  }

  management {
    auto_upgrade = true
    auto_repair  = true
  }

  node_config {
    preemptible  = false
    machine_type = var.machine_type
    disk_size_gb = var.disk_size
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
