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

# Ingress
variable "cluster_ingress" {
  description = "Path to the cluster-ingress Helm chart"
  type        = string
  nullable    = false
}

variable "cluster_ingress_values" {
  description = "Path to values for the cluster-ingress Helm chart"
  type        = string
  nullable    = false
}
