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

########################################################################################
# AKS Cluster
########################################################################################

resource "azurerm_resource_group" "cluster" {
  name     = var.resource_group_name
  location = var.azure_location
}

resource "azurerm_kubernetes_cluster" "cluster" {
  name                = var.cluster_name
  location            = azurerm_resource_group.cluster.location
  resource_group_name = azurerm_resource_group.cluster.name
  dns_prefix          = "${var.cluster_name}-dns"
  kubernetes_version  = "1.33.3"

  role_based_access_control_enabled = true

  default_node_pool {
    name                 = "primarynp"
    vm_size              = "Standard_D4_v3"
    node_count           = 1
    min_count            = 1
    max_count            = 2
    auto_scaling_enabled = true
    vnet_subnet_id       = data.azurerm_subnet.aks.id

    node_labels = {
      role = var.application_node_label
    }
  }

  network_profile {
    # outbound_type     = "userAssignedNATGateway"
    network_plugin    = "azure"
    outbound_type     = "loadBalancer"
    load_balancer_sku = "standard"
    service_cidr      = "172.16.0.0/16"
    dns_service_ip    = "172.16.0.10"
  }

  identity {
    type = "SystemAssigned"
  }
}

########################################################################################
# Additional Node Pool for Monitoring
########################################################################################

resource "azurerm_kubernetes_cluster_node_pool" "monitoring_nodes" {
  name                  = "monitoringnp"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.cluster.id
  vm_size               = "Standard_D2_v3"
  node_count            = 1
  auto_scaling_enabled  = false
  vnet_subnet_id        = data.azurerm_subnet.aks.id
  node_labels = {
    role = var.monitoring_node_label
  }
}
