########################################################################################
# Project: 
#   Managed Kubernetes Services: A Comparison of AKS, EKS and GKE
#
# Author:  
#   Michał Ziemianek
#
# Description:
#   The project focuses on deploying and benchmarking
#   a microservices-based application using Kubernetes and cloud-native technologies
#   (Terraform, Ansible, Helm, Prometheus, Grafana, K6).
#
# License:
#   Apache 2.0
#
# Notes:
#   - This code is intended for educational and research purposes.
#   - Ensure proper configuration of cloud resources before execution.
#
# © 2025 Michał Ziemianek. All rights reserved.
########################################################################################

# Subnet for nodes + secondary ranges for Pods/Services
resource "google_compute_subnetwork" "subnet" {
  name          = var.subnet_name
  ip_cidr_range = var.subnet_cidr
  region        = var.region
  network       = data.google_compute_network.vpc_network.id

  secondary_ip_range {
    range_name    = "pods"
    ip_cidr_range = "10.20.0.0/16"
  }

  secondary_ip_range {
    range_name    = "services"
    ip_cidr_range = "10.30.0.0/20"
  }
}

# Allow internal communication between nodes
resource "google_compute_firewall" "allow_internal_traffic" {
  name    = "allow-internal-traffic"
  network = data.google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["0-65535"]
  }

  source_ranges = [var.subnet_cidr]
}

# Allow HTTPS ingress (for frontend / LB)
resource "google_compute_firewall" "allow_external_ingress" {
  name    = "allow-external-ingress"
  network = data.google_compute_network.vpc_network.name

  allow {
    protocol = "tcp"
    ports    = ["443"]
  }

  source_ranges = ["0.0.0.0/0"]
}

resource "google_compute_router" "nat_router" {
  name    = "${var.cluster_name}-nat-router"
  region  = var.region
  network = data.google_compute_network.vpc_network.id
}

resource "google_compute_router_nat" "nat_config" {
  name   = "${var.cluster_name}-nat"
  router = google_compute_router.nat_router.name
  region = google_compute_router.nat_router.region

  nat_ip_allocate_option = "AUTO_ONLY"

  source_subnetwork_ip_ranges_to_nat = "LIST_OF_SUBNETWORKS"

  subnetwork {
    name                    = google_compute_subnetwork.subnet.name
    source_ip_ranges_to_nat = ["ALL_IP_RANGES"]
  }

  log_config {
    enable = true
    filter = "ERRORS_ONLY"
  }
}

# GKE cluster (VPC-native, private nodes)
resource "google_container_cluster" "primary" {
  name                     = var.cluster_name
  location                 = var.region
  remove_default_node_pool = true
  initial_node_count       = 1
  deletion_protection      = false

  networking_mode = "VPC_NATIVE"
  network         = data.google_compute_network.vpc_network.name
  subnetwork      = google_compute_subnetwork.subnet.name

  # Keep single-zone for cost/reproducibility
  node_locations = ["${var.region}-a"]

  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
  }

  ip_allocation_policy {
    cluster_secondary_range_name  = "pods"     # must match subnet
    services_secondary_range_name = "services" # must match subnet
  }

  private_cluster_config {
    enable_private_nodes    = true
    enable_private_endpoint = false
    master_ipv4_cidr_block  = "192.168.0.0/28"
  }
}

# Node pool
resource "google_container_node_pool" "primary_nodes" {
  name     = "${var.cluster_name}-node-pool"
  cluster  = google_container_cluster.primary.name
  location = var.region

  node_locations = ["${var.region}-a"]

  initial_node_count = 3 # 3 nodes baseline

  autoscaling {
    total_min_node_count = 3 # fix at 3 for fairness
    total_max_node_count = 3
  }

  management {
    auto_upgrade = true
    auto_repair  = true
  }

  node_config {
    preemptible  = false # on-demand for fairness baseline
    machine_type = var.machine_type
    disk_size_gb = 50
    disk_type    = "pd-balanced"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
