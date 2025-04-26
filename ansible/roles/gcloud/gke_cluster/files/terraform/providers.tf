terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.27.0"
    }
  }

  required_version = ">= 1.11.3"

  backend "gcs" {}
}

provider "google" {
  project = var.project_id
  region  = var.region
}
