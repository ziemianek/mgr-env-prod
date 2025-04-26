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
  namespace  = helm_release.istio_base.namespace
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
  values = ["${file(var.cluster_ingress_values)}"]
}
