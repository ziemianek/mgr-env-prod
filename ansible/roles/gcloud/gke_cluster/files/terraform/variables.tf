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

variable "machine_type" {
  description = "Machine type for the node pool"
  type        = string
  nullable    = false
}

variable "disk_size" {
  description = "Disk size in GB for the node pool"
  type        = number
  nullable    = false
}
