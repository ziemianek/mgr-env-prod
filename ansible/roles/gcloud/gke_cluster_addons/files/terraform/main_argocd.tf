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
