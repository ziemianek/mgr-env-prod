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

variable "location_name" {
  description = "The region where resources will be created."
  type        = string
  nullable    = false
}

variable "tfstate_resource_group_name" {
  description = "Resource group name for tfstate storage account"
  type        = string
  nullable    = false
}

variable "tfstate_storage_account_name" {
  description = "Storage account name for tfstate"
  type        = string
  nullable    = false
}

variable "tfstate_container_name" {
  description = "Storage container name for tfstate"
  type        = string
  nullable    = false
}
