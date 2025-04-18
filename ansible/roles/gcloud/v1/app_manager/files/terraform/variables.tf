variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
  nullable    = false
}

variable "region" {
  description = "GCP region"
  type        = string
  nullable    = false
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  nullable    = false
}

variable "namespace" {
  description = "Namespace for the application"
  type        = string
  nullable    = false
}
