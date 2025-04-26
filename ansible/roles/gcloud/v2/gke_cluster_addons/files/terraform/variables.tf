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

# Addons
variable "cert_manager" {
  description = "Path to the cert-manager Helm chart"
  type        = string
  nullable    = false
}

variable "istiod" {
  description = "Path to the istiod Helm chart"
  type        = string
  nullable    = false
}

variable "istio_base" {
  description = "Path to the istio-base Helm chart"
  type        = string
  nullable    = false
}

variable "istio_gateway" {
  description = "Path to the istio-gateway Helm chart"
  type        = string
  nullable    = false
}