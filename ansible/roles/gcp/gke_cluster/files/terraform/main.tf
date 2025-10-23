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
# NAT Gateway and public HTTPS ingress
########################################################################################

resource "azurerm_subnet" "subnet" {
  name                 = var.subnet_name
  resource_group_name  = var.resource_group_name
  virtual_network_name = data.azurerm_virtual_network.vnet.name
  address_prefixes     = [var.subnet_cidr]
}

# Public IP for NAT Gateway (egress)
resource "azurerm_public_ip" "nat_gateway" {
  name                = "${var.cluster_name}-nat-pip"
  location            = var.azure_location
  resource_group_name = var.resource_group_name
  allocation_method   = "Static"
  sku                 = "Standard"
}

resource "azurerm_nat_gateway" "nat_gateway" {
  name                = "${var.cluster_name}-nat-gw"
  location            = var.azure_location
  resource_group_name = var.resource_group_name
  sku_name            = "Standard"
}

resource "azurerm_nat_gateway_public_ip_association" "nat_gateway" {
  nat_gateway_id       = azurerm_nat_gateway.nat_gateway.id
  public_ip_address_id = azurerm_public_ip.nat_gateway.id
}

resource "azurerm_subnet_nat_gateway_association" "nat_assoc" {
  subnet_id      = azurerm_subnet.subnet.id
  nat_gateway_id = azurerm_nat_gateway.nat_gateway.id
}

########################################################################################
# Network Security Group (allow inbound HTTPS)
########################################################################################

resource "azurerm_network_security_group" "aks_nsg" {
  name                = "${var.cluster_name}-nsg"
  location            = var.azure_location
  resource_group_name = var.resource_group_name

  security_rule {
    name                       = "allow_https_inbound"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
    description                = "Allow inbound HTTPS traffic to Ingress Controller"
  }

  # (optional) if you want to allow HTTP too
  # security_rule {
  #   name                       = "allow_http_inbound"
  #   priority                   = 110
  #   direction                  = "Inbound"
  #   access                     = "Allow"
  #   protocol                   = "Tcp"
  #   source_port_range          = "*"
  #   destination_port_range     = "80"
  #   source_address_prefix      = "*"
  #   destination_address_prefix = "*"
  #   description                = "Allow inbound HTTP traffic to Ingress Controller"
  # }

  security_rule {
    name                       = "allow_egress_internet"
    priority                   = 200
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "Internet"
    description                = "Allow outbound Internet traffic"
  }
}

# Attach NSG to subnet
resource "azurerm_subnet_network_security_group_association" "aks_nsg_assoc" {
  subnet_id                 = azurerm_subnet.subnet.id
  network_security_group_id = azurerm_network_security_group.aks_nsg.id
}

########################################################################################
# AKS Cluster
########################################################################################

resource "azurerm_kubernetes_cluster" "primary" {
  depends_on = [
    azurerm_subnet_nat_gateway_association.nat_assoc,
    azurerm_subnet_network_security_group_association.aks_nsg_assoc
  ]

  name                = var.cluster_name
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  dns_prefix          = "${var.cluster_name}-dns"

  default_node_pool {
    name                 = "primarynp"
    vm_size              = "Standard_D4_v3"
    node_count           = 1
    min_count            = 1
    max_count            = 2
    auto_scaling_enabled = true
    vnet_subnet_id       = azurerm_subnet.subnet.id
    node_labels = {
      role = var.application_node_label
    }
  }

  network_profile {
    network_plugin    = "azure"
    outbound_type     = "userDefinedRouting"
    load_balancer_sku = "standard"
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
  kubernetes_cluster_id = azurerm_kubernetes_cluster.primary.id
  vm_size               = "Standard_D2_v3"
  node_count            = 1
  min_count             = 1
  max_count             = 1
  auto_scaling_enabled  = false
  vnet_subnet_id        = azurerm_subnet.subnet.id
  node_labels = {
    role = var.monitoring_node_label
  }
}
