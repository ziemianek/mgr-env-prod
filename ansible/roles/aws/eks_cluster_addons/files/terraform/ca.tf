resource "aws_iam_role" "ca" {
  name               = "eks-cluster-autoscaler-irsa"
  assume_role_policy = data.aws_iam_policy_document.ca_trust.json
}

resource "aws_iam_policy" "cluster_autoscaler" {
  name   = "EKS-Cluster-Autoscaler-Policy"
  policy = data.aws_iam_policy_document.cluster_autoscaler.json
}

resource "aws_iam_role_policy_attachment" "ca_attach" {
  role       = aws_iam_role.ca.name
  policy_arn = aws_iam_policy.cluster_autoscaler.arn
}
