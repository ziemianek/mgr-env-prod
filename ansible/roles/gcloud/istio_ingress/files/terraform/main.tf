resource "kubernetes_namespace" "app" {
  metadata {
    name = var.namespace

    labels = {
      istio-injection = "enabled"
    }
  }
}
