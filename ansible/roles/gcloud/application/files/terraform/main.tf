resource "helm_release" "boutique" {
  name      = "boutique"
  chart     = var.application_helm_chart_path
  namespace = "boutique"

  create_namespace = true
}
