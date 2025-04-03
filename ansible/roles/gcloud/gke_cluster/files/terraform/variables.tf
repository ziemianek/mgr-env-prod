variable "project_id" {
  description = "Google Cloud project ID"
  type        = string
  nullable    = false
}

variable "region" {
  description = "GCP region"
  type        = string
  nullable    = false
}

variable "vpc_name" {
  description = "VPC network name"
  type        = string
  nullable    = false
}

variable "subnet_name" {
  description = "Subnet name"
  type        = string
  nullable    = false
}

variable "cluster_name" {
  description = "GKE cluster name"
  type        = string
  nullable    = false
}

variable "node_count" {
  description = "Number of nodes in the node pool"
  type        = number
  nullable    = false
}
