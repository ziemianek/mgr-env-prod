resource "google_container_cluster" "primary" {
  name     = var.cluster_name
  location = "${var.region}-a" # disable multi-zone for testing

  remove_default_node_pool = true
  initial_node_count       = 1

  deletion_protection = false

  networking_mode = "VPC_NATIVE"
  network         = var.vpc_name
  subnetwork      = var.subnet_name
  ip_allocation_policy {}
}

resource "google_container_node_pool" "primary_nodes" {
  name       = "${var.cluster_name}-node-pool"
  cluster    = google_container_cluster.primary.name
  location   = "${var.region}-a" # disable multi-zone for testing
  node_count = var.node_count

  node_config {
    machine_type = "e2-medium"
    disk_size_gb = 20
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}
