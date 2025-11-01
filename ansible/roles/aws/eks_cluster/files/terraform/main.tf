########################################################################################
# Project: 
#   Managed Kubernetes Services: A Comparison of AKS, EKS and GKE
#
# Author:  
#   Michał Ziemianek
#
# Description:
#   Deploys an Amazon EKS cluster for benchmarking a microservices-based application
#   using Kubernetes and cloud-native technologies (Terraform, Ansible, Helm, Prometheus, Grafana, K6).
#
# License:
#   Apache 2.0
#
# Notes:
#   - This configuration uses the official terraform-aws-modules/eks/aws module.
#   - It preserves the logic from the previous manual setup (two node groups, IAM roles, etc.).
#   - Ensure VPC and subnets exist before deployment.
#
# © 2025 Michał Ziemianek. All rights reserved.
########################################################################################

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 21.0"

  name               = var.cluster_name
  kubernetes_version = "1.33"

  # disable EKS auto mode
  compute_config = {
    enabled = false
  }

  # Add-ons required for networking, DNS, and observability
  addons = {
    vpc-cni                         = { before_compute = true }
    kube-proxy                      = {}
    coredns                         = {}
    eks-pod-identity-agent          = { before_compute = true }
    amazon-cloudwatch-observability = {}
  }

  # Networking
  vpc_id     = data.aws_vpc.main.id
  subnet_ids = data.aws_subnets.private.ids

  # Public API access for testing purposes
  endpoint_public_access = true

  # Add the creator as cluster admin
  enable_cluster_creator_admin_permissions = true

  eks_managed_node_groups = {
    primary-node-group = {
      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = ["t3.xlarge"]
      force_delete   = true

      min_size     = 1
      max_size     = 2
      desired_size = 1

      labels = {
        role = var.application_node_label
      }
    }

    monitoring-node-group = {
      ami_type       = "AL2023_x86_64_STANDARD"
      instance_types = ["t3.large"]
      force_delete   = true

      min_size     = 1
      max_size     = 1
      desired_size = 1

      labels = {
        role = var.monitoring_node_label
      }
    }
  }

  # EKS K8s API cluster needs to be able to talk with the EKS worker nodes with port 15017/TCP and 15012/TCP which is used by Istio
  # Istio in order to create sidecar needs to be able to communicate with webhook and for that network passage to EKS is needed.
  # Source: https://github.com/aws-ia/terraform-aws-eks-blueprints/blob/main/patterns/istio/main.tf
  node_security_group_additional_rules = {
    ingress_15017 = {
      description                   = "Cluster API - Istio Webhook namespace.sidecar-injector.istio.io"
      protocol                      = "TCP"
      from_port                     = 15017
      to_port                       = 15017
      type                          = "ingress"
      source_cluster_security_group = true
    }
    ingress_15012 = {
      description                   = "Cluster API to nodes ports/protocols"
      protocol                      = "TCP"
      from_port                     = 15012
      to_port                       = 15012
      type                          = "ingress"
      source_cluster_security_group = true
    }
  }
}
