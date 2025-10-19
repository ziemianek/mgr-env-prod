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

resource "azurerm_subnet" "subnet" {
  name                 = var.subnet_name
  resource_group_name  = data.azurerm_resource_group.rg.name
  virtual_network_name = data.azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_cidr]
}

resource "azurerm_public_ip" "nat_pip" {
  name                = "${var.cluster_name}-nat-pip"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_nat_gateway" "nat_gateway" {
  name                  = "${var.cluster_name}-nat-gateway"
  location              = data.azurerm_resource_group.rg.location
  resource_group_name   = data.azurerm_resource_group.rg.name
  sku_name              = "Standard"
  public_ip_address_ids = [azurerm_public_ip.nat_pip.id]
}

resource "azurerm_subnet_nat_gateway_association" "nat_assoc" {
  subnet_id      = azurerm_subnet.subnet.id
  nat_gateway_id = azurerm_nat_gateway.nat_gateway.id
}

resource "azurerm_kubernetes_cluster" "primary" {
  name                = var.cluster_name
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  dns_prefix          = "${var.cluster_name}-dns"

  default_node_pool {
    name           = "default"
    node_count     = 1
    vm_size        = "Standard_D2_v2"
    vnet_subnet_id = azurerm_subnet.subnet.id
  }

  network_profile {
    network_plugin = "azure"
    outbound_type  = "userDefinedRouting"
    load_balancer_sku = "standard"
  }

  identity {
    type = "SystemAssigned"
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "primary_nodes" {
  name                  = "appnodepool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.primary.id
  vm_size               = "Standard_D4_v3" # Equivalent to e2-standard-4
  node_count            = 1
  min_count             = 1
  max_count             = 2
  enable_auto_scaling   = true
  vnet_subnet_id        = azurerm_subnet.subnet.id

  node_labels = {
    role = var.application_node_label
  }
}

resource "azurerm_kubernetes_cluster_node_pool" "monitoring_nodes" {
  name                  = "monnodepool"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.primary.id
  vm_size               = "Standard_D2_v3" # Equivalent to e2-standard-2
  node_count            = 1
  min_count             = 1
  max_count             = 1
  enable_auto_scaling   = true
  vnet_subnet_id        = azurerm_subnet.subnet.id

  node_labels = {
    role = var.monitoring_node_label
  }
}
