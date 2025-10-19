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

resource "azurerm_resource_group" "tfstate_rg" {
  name     = var.tfstate_resource_group_name
  location = var.location_name
}

resource "azurerm_storage_account" "tfstate_sa" {
  name                     = var.tfstate_storage_account_name
  resource_group_name      = azurerm_resource_group.tfstate_rg.name
  location                 = azurerm_resource_group.tfstate_rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_storage_container" "tfstate_sc" {
  name                  = var.tfstate_container_name
  storage_account_id    = azurerm_storage_account.tfstate_sa.id
  container_access_type = "private"
}
