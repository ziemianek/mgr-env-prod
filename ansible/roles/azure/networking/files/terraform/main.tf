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
# Networking for AKS
########################################################################################

resource "azurerm_resource_group" "networking" {
  name     = var.resource_group_name
  location = var.azure_location
}

resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  location            = var.azure_location
  resource_group_name = azurerm_resource_group.networking.name
  address_space       = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "aks" {
  name                 = var.subnet_name
  resource_group_name  = azurerm_resource_group.networking.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = ["10.0.0.0/20"]
}

# resource "azurerm_nat_gateway" "nat_gateway" {
#   name                = "${var.app_name}-aks-nat-gw"
#   location            = var.azure_location
#   resource_group_name = azurerm_resource_group.networking.name
#   sku_name            = "Standard"
# }

# resource "azurerm_public_ip" "nat_gateway" {
#   name                = "${var.app_name}-aks-nat-pip"
#   location            = var.azure_location
#   resource_group_name = azurerm_resource_group.networking.name
#   allocation_method   = "Static"
#   sku                 = "Standard"
# }

# resource "azurerm_nat_gateway_public_ip_association" "nat_gateway" {
#   nat_gateway_id       = azurerm_nat_gateway.nat_gateway.id
#   public_ip_address_id = azurerm_public_ip.nat_gateway.id
# }

########################################################################################
# NSG
########################################################################################

resource "azurerm_network_security_group" "aks_nsg" {
  name                = "${var.app_name}-aks-network-sg"
  location            = var.azure_location
  resource_group_name = azurerm_resource_group.networking.name

  security_rule {
    name                       = "allow_https_inbound"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "443"
    source_address_prefix      = "0.0.0.0/0"
    destination_address_prefix = "*"
    description                = "Allow inbound HTTPS traffic from Internet to Ingress Controller"
  }

  security_rule {
    name                       = "allow_lb_probe"
    priority                   = 110
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "15021"
    source_address_prefix      = "168.63.129.16/32"
    destination_address_prefix = "*"
    description                = "Allow inbound health probe traffic from Azure LB"
  }

  security_rule {
    name                       = "allow_egress_internet"
    priority                   = 120
    direction                  = "Outbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
    description                = "Allow outbound Internet traffic"
  }
}

resource "azurerm_subnet_network_security_group_association" "aks_nsg_assoc" {
  subnet_id                 = azurerm_subnet.aks.id
  network_security_group_id = azurerm_network_security_group.aks_nsg.id
}
