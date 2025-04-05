data "google_container_cluster" "gke_cluster" {
  name     = var.cluster_name
  location = var.region
}
