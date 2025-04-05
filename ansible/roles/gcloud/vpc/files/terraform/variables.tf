variable "project_id" {
  description = "The ID of the GCP project where resources will be created."
  type        = string
  nullable    = false
}

variable "region" {
  description = "The region where resources will be created."
  type        = string
  nullable    = false
}

variable "vpc_name" {
  description = "The name of the VPC network."
  type        = string
  nullable    = false
}

variable "vpc_cidr" {
  description = "The CIDR range for the VPC network."
  type        = string
  nullable    = false
}

variable "subnet_name" {
  description = "The name of the subnet."
  type        = string
  nullable    = false
}
