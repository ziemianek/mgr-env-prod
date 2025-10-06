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

resource "helm_release" "istio_base" {
  name      = "istio-base"
  chart     = var.istio_base
  namespace = "istio-system"

  create_namespace = true

  set {
    name  = "global.istioNamespace"
    value = "istio-system"
  }
}

resource "helm_release" "istiod" {
  name       = "istiod"
  chart      = var.istiod
  namespace  = "istio-system"
  depends_on = [helm_release.istio_base]

  set {
    name  = "global.istioNamespace"
    value = "istio-system"
  }

  set {
    name  = "telemetry.enabled"
    value = "true"
  }

  set {
    name  = "meshConfig.ingressService"
    value = "istio-ingress-gateway"
  }
}

resource "helm_release" "istio_ingress_gateway" {
  name       = "istio-ingress-gateway"
  chart      = var.istio_gateway
  namespace  = "istio-ingress"
  depends_on = [helm_release.istiod]

  create_namespace = true
}

resource "helm_release" "cert_manager" {
  name      = "cert-manager"
  chart     = var.cert_manager
  namespace = "cert-manager"

  create_namespace = true
}

resource "helm_release" "cluster_ingress" {
  name      = "cluster-ingress"
  chart     = var.cluster_ingress
  namespace = "istio-ingress"

  depends_on = [
    helm_release.istio_ingress_gateway,
    helm_release.cert_manager
  ]

  values = ["${file(var.values_cluster_ingress)}"]
}

resource "helm_release" "kube_prometheus_stack" {
  name      = "kube-prometheus-stack"
  chart     = var.kube_prometheus_stack
  namespace = "monitoring"

  create_namespace = true

  values = ["${file(var.values_kube_prometheus_stack)}"]
}
