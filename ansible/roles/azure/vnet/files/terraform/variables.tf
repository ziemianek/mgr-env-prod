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

variable "resource_group_name" {
  description = "The name of the resource group."
  type        = string
  nullable    = false
}

variable "location" {
  description = "The region where resources will be created."
  type        = string
  nullable    = false
}

variable "vpc_name" {
  description = "The name of the VPC network."
  type        = string
  nullable    = false
}
