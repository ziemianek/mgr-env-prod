terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.27.0"
    }

    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.36.0"
    }
  }

  required_version = ">= 1.11.3"

  backend "gcs" {}
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# TODO: enhance provider config
provider "kubernetes" {
  host  = "https://${data.google_container_cluster.gke_cluster.endpoint}"
  token = data.google_client_config.default.access_token
  cluster_ca_certificate = base64decode(
    data.google_container_cluster.gke_cluster.master_auth[0].cluster_ca_certificate
  )
}
