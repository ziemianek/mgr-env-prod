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


variable "app_name" {
  description = "Name of the application"
  type        = string
  nullable    = false
}

variable "resource_group_name" {
  description = "Azure resource group name"
  type        = string
  nullable    = false
}

variable "azure_location" {
  description = "Azure region"
  type        = string
  nullable    = false
}

variable "vnet_name" {
  description = "VNet name"
  type        = string
  nullable    = false
}

variable "subnet_name" {
  description = "Subnet name"
  type        = string
  nullable    = false
}

variable "cluster_name" {
  description = "AKS cluster name"
  type        = string
  nullable    = false
}

variable "monitoring_node_label" {
  description = "Label for node where monitoring components live"
  type        = string
  nullable    = false
}

variable "application_node_label" {
  description = "Label for node where application live"
  type        = string
  nullable    = false
}
