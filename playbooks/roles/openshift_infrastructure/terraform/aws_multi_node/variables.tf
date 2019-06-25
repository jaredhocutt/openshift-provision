variable "bastion_hostname" {
  type        = string
  description = "The hostname for the bastion node (e.g. bastion.openshift.example.com)"
}

variable "openshift_cluster_id" {
  type        = string
  description = "A cluster ID that is unique to the AWS account (e.g. openshift.example-com)"
}

variable "openshift_public_hostname" {
  type        = string
  description = "The hostname for the external OpenShift API (e.g. openshift.example.com)"
}

variable "openshift_internal_hostname" {
  type        = string
  description = "The hostname for the internal OpenShift API (e.g. openshift-internal.example.com)"
}

variable "openshift_apps_subdomain" {
  type        = string
  description = "The wildcard domain for the OpenShift router (e.g. *.apps.openshift.example.com)"
}

variable "cloud_access_enabled" {
  type        = bool
  default     = false
  description = "If cloud access is enabled on the AWS account, set to true to prevent being double charged for RHEL"
}

variable "route53_hosted_zone_id" {
  type        = string
  description = "The ID of the Route53 hosted zone to create the OpenShift hostnames provided"
}

variable "vpc_cidr_block" {
  type        = string
  default     = "192.168.3.0/24"
  description = "The CIDR to assign to the VPC"
}

variable "aws_keypair" {
  type        = string
  description = "The name of the AWS keypair to insert into the EC2 instances"
}

variable "instance_type_master" {
  type        = string
  default     = "m5.xlarge"
  description = "The EC2 instance type for the master node (e.g. m5.xlarge)"
}

variable "instance_type_infra" {
  type        = string
  default     = "m5.xlarge"
  description = "The EC2 instance type for the infra node (e.g. m5.xlarge)"
}

variable "instance_type_compute" {
  type        = string
  default     = "m5.large"
  description = "The EC2 instance type for the compute nodes (e.g. m5.large)"
}

variable "root_block_device_size" {
  type        = number
  default     = 60
  description = "The size in GB of the root disk for each EC2 instance"
}

variable "instance_count_compute" {
  type        = number
  default     = 3
  description = "The number of compute instanes"
}

variable "ocs_total_capacity" {
  type        = number
  default     = 250
  description = "The total amount of storage in GB for OpenShift Container Storage (OCS)"
}
