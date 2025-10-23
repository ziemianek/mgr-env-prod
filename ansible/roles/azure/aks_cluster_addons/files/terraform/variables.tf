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

variable "cluster_name" {
  description = "AKS cluster name"
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

variable "values_cluster_ingress" {
  description = "Path to values for the cluster-ingress Helm chart"
  type        = string
  nullable    = false
}

# Monitoring
variable "kube_prometheus_stack" {
  description = "Path to the kube-prometheus-stack Helm chart"
  type        = string
  nullable    = false
}

variable "values_kube_prometheus_stack" {
  description = "Path to values for the kube-prometheus-stack Helm chart"
  type        = string
  nullable    = false
}

variable "monitoring_namespace" {
  description = "Namespace where monitoring components live"
  type        = string
  nullable    = false
}
