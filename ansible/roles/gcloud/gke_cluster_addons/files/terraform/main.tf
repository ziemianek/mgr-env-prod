# ArgoCD
resource "helm_release" "argocd" {
  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm/"
  chart      = "argo-cd"
  version    = "7.8.23"

  namespace        = "argocd"
  create_namespace = true
}

# Istio
resource "helm_release" "istio_base" {
  name       = "istio-base"
  repository = "https://istio-release.storage.googleapis.com/charts"
  chart      = "base"
  version    = "1.25.0"

  namespace        = "istio-system"
  create_namespace = true

  set {
    name  = "global.istioNamespace"
    value = "istio-system"
  }
}

resource "helm_release" "istiod" {
  name       = "istiod"
  repository = "https://istio-release.storage.googleapis.com/charts"
  chart      = "istiod"
  version    = "1.25.0"
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
  repository = "https://istio-release.storage.googleapis.com/charts"
  chart      = "gateway"
  version    = "1.25.0"

  namespace        = "istio-ingress"
  create_namespace = true

  depends_on = [helm_release.istiod]
}
# =====

# Cert-manager
resource "helm_release" "cert_manager" {
  name       = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  version    = "v1.17.1"

  namespace        = "cert-manager"
  create_namespace = true
}
