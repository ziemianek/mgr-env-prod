# Tworzenie roli IAM dla Cluster Autoscalera
resource "aws_iam_role" "ca" {
  name               = "eks-cluster-autoscaler-irsa"
  assume_role_policy = data.aws_iam_policy_document.ca_trust.json
}

# Tworzenie polityki z dokumentu data.tf
resource "aws_iam_policy" "cluster_autoscaler" {
  name   = "EKS-Cluster-Autoscaler-Policy"
  policy = data.aws_iam_policy_document.cluster_autoscaler.json
}

# Przypisanie polityki do roli
resource "aws_iam_role_policy_attachment" "ca_attach" {
  role       = aws_iam_role.ca.name
  policy_arn = aws_iam_policy.cluster_autoscaler.arn
}

# resource "kubernetes_service_account" "ca" {
#   depends_on = [
#     aws_iam_role_policy_attachment.ca_attach
#   ]

#   metadata {
#     name      = "cluster-autoscaler"
#     namespace = "kube-system"
#     annotations = {
#       "eks.amazonaws.com/role-arn" = aws_iam_role.ca.arn
#     }
#     labels = {
#       "app.kubernetes.io/name" = "cluster-autoscaler"
#     }
#   }
#   automount_service_account_token = true
# }
