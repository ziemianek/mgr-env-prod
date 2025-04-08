# ArgoCD
resource "kubernetes_namespace" "argocd" {
  metadata {
    name = "argocd"
  }
}

resource "helm_release" "argocd" {
  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm/"
  chart      = "argo-cd"
  version    = "7.8.23"
  namespace  = kubernetes_namespace.argocd.metadata[0].name
}


resource "kubernetes_namespace" "istio_system" {
  metadata {
    name = "istio-system"
  }
}

# Istio
resource "helm_release" "istio_base" {
  name       = "istio-base"
  repository = "https://istio-release.storage.googleapis.com/charts"
  chart      = "base"
  version    = "1.25.0"
  namespace  = kubernetes_namespace.istio_system.metadata[0].name

  create_namespace = false
}

resource "helm_release" "istiod" {
  name       = "istiod"
  repository = "https://istio-release.storage.googleapis.com/charts"
  chart      = "istiod"
  version    = "1.25.0"
  namespace  = kubernetes_namespace.istio_system.metadata[0].name

  depends_on = [helm_release.istio_base]
}

# I would love to use this but too much work for now
# Id have to separate everything into separate files
# Since i cannot deploy manifest that contains multiple resources separated by ---
# # Istio Addons
# resource "kubernetes_manifest" "prometheus" {
#   manifest   = yamldecode(file("../manifests/istio_addons/prometheus.yaml"))
#   depends_on = [helm_release.istiod]
# }

# resource "kubernetes_manifest" "grafana" {
#   manifest   = yamldecode(file("../manifests/istio_addons/grafana.yaml"))
#   depends_on = [helm_release.istiod]
# }

# resource "kubernetes_manifest" "kiali" {
#   manifest   = yamldecode(file("../manifests/istio_addons/kiali.yaml"))
#   depends_on = [helm_release.istiod]
# }

# # Cert Manager
# resource "kubernetes_manifest" "cert_manager_issuer" {
#   manifest = yamldecode(file("../manifests/cert_manager/cluster_issuer.yaml"))
# }

# resource "kubernetes_manifest" "cert_manager_certificate" {
#   manifest = yamldecode(file("../manifests/cert_manager/certificate.yaml"))
# }

# # Chaos Mesh
# resource "kubernetes_manifest" "chaos_mesh" {
#   manifest = yamldecode(file("../manifests/chaos_mesh/chaos_mesh.yaml"))
# }
