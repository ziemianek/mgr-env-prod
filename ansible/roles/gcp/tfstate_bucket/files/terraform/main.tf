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

resource "google_storage_bucket" "tfstate" {
  name                        = var.tfstate_bucket_name
  location                    = "EU"
  force_destroy               = false
  uniform_bucket_level_access = true
  versioning {
    enabled = true
  }
}

resource "google_storage_bucket_iam_member" "tfstate_admin" {
  bucket = google_storage_bucket.tfstate.name
  role   = "roles/storage.admin"
  member = "serviceAccount:${var.client_email}"
}
