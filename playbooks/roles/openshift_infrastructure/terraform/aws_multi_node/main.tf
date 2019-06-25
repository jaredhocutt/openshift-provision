terraform {
  backend "s3" {}
}

provider "aws" {}

###############################################################################
# Data
###############################################################################

locals {
  instance_tags = "${map("kubernetes.io/cluster/${var.openshift_cluster_id}", "${var.openshift_cluster_id}")}"
}

data "aws_ami" "rhel7" {
  most_recent = true
  owners      = ["309956199498"] # Red Hat

  filter {
    name   = "name"
    values = ["RHEL-7.6_HVM_GA-20190128-x86_64-0-${var.cloud_access_enabled == true ? "Access2" : "Hourly2"}-GP2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

###############################################################################
# VPC
###############################################################################

resource "aws_vpc" "openshift" {
  cidr_block           = "${var.vpc_cidr_block}"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "${var.openshift_cluster_id}"
  }
}

resource "aws_vpc_dhcp_options" "default" {
  domain_name_servers = ["AmazonProvidedDNS"]
}

resource "aws_vpc_dhcp_options_association" "default" {
  vpc_id          = "${aws_vpc.openshift.id}"
  dhcp_options_id = "${aws_vpc_dhcp_options.default.id}"
}

resource "aws_internet_gateway" "default" {
  vpc_id = "${aws_vpc.openshift.id}"

  tags = {
    Name = "${var.openshift_cluster_id}"
  }
}

resource "aws_subnet" "public" {
  vpc_id                  = "${aws_vpc.openshift.id}"
  cidr_block              = "${var.vpc_cidr_block}"
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.openshift_cluster_id}-public"
  }
}

resource "aws_route" "default" {
  route_table_id = "${aws_vpc.openshift.default_route_table_id}"

  destination_cidr_block = "0.0.0.0/0"
  gateway_id = "${aws_internet_gateway.default.id}"
}

###############################################################################
# Security Groups
###############################################################################

resource "aws_security_group" "ssh" {
  name        = "${var.openshift_cluster_id}-ssh"
  description = "${var.openshift_cluster_id}-ssh"
  vpc_id      = "${aws_vpc.openshift.id}"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "api" {
  name        = "${var.openshift_cluster_id}-api"
  description = "${var.openshift_cluster_id}-api"
  vpc_id      = "${aws_vpc.openshift.id}"

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "router" {
  name        = "${var.openshift_cluster_id}-router"
  description = "${var.openshift_cluster_id}-router"
  vpc_id      = "${aws_vpc.openshift.id}"

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

resource "aws_security_group" "cluster" {
  name        = "${var.openshift_cluster_id}-cluster"
  description = "${var.openshift_cluster_id}-cluster"
  vpc_id      = "${aws_vpc.openshift.id}"

  egress {
    from_port       = 0
    to_port         = 0
    protocol        = "-1"
    cidr_blocks     = ["0.0.0.0/0"]
  }
}

resource "aws_security_group_rule" "cluster_allow_all" {
  type              = "ingress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  security_group_id = "${aws_security_group.cluster.id}"
  self              = true
}

###############################################################################
# EC2 Instances
###############################################################################

resource "aws_instance" "master" {
  ami                    = "${data.aws_ami.rhel7.id}"
  instance_type          = "${var.instance_type_master}"
  key_name               = "${var.aws_keypair}"
  subnet_id              = "${aws_subnet.public.id}"
  vpc_security_group_ids = ["${aws_security_group.cluster.id}", "${aws_security_group.api.id}", "${aws_security_group.ssh.id}"]

  root_block_device {
    volume_size           = "${var.root_block_device_size}"
    delete_on_termination = true
  }

  tags = "${merge(
    local.instance_tags,
    map(
      "Name", "${var.openshift_cluster_id}-master"
    )
  )}"
}

resource "aws_instance" "infra" {
  ami                    = "${data.aws_ami.rhel7.id}"
  instance_type          = "${var.instance_type_infra}"
  key_name               = "${var.aws_keypair}"
  subnet_id              = "${aws_subnet.public.id}"
  vpc_security_group_ids = ["${aws_security_group.cluster.id}", "${aws_security_group.router.id}", "${aws_security_group.ssh.id}"]

  root_block_device {
    volume_size           = "${var.root_block_device_size}"
    delete_on_termination = true
  }

  tags = "${merge(
    local.instance_tags,
    map(
      "Name", "${var.openshift_cluster_id}-infra"
    )
  )}"
}

resource "aws_instance" "compute" {
  ami                    = "${data.aws_ami.rhel7.id}"
  instance_type          = "${var.instance_type_compute}"
  key_name               = "${var.aws_keypair}"
  subnet_id              = "${aws_subnet.public.id}"
  vpc_security_group_ids = ["${aws_security_group.cluster.id}", "${aws_security_group.ssh.id}"]
  count                  = "${var.instance_count_compute}"

  root_block_device {
    volume_size           = "${var.root_block_device_size}"
    delete_on_termination = true
  }

  ebs_block_device {
    device_name           = "/dev/sdb"
    volume_type           = "gp2"
    volume_size           = "${(var.ocs_total_capacity * 3) / var.instance_count_compute}"
    delete_on_termination = true
  }

  tags = "${merge(
    local.instance_tags,
    map(
      "Name", "${var.openshift_cluster_id}-${format("compute%02d", count.index)}"
    )
  )}"
}

###############################################################################
# Elastic IPs
###############################################################################

resource "aws_eip" "master" {
  vpc        = true
  instance   = "${aws_instance.master.id}"
  depends_on = ["aws_internet_gateway.default"]

  tags = {
    Name = "${var.openshift_cluster_id}-master"
  }
}

resource "aws_eip" "infra" {
  vpc        = true
  instance   = "${aws_instance.infra.id}"
  depends_on = ["aws_internet_gateway.default"]

  tags = {
    Name = "${var.openshift_cluster_id}-infra"
  }
}

###############################################################################
# DNS Entries
###############################################################################

resource "aws_route53_record" "bastion" {
  zone_id = "${var.route53_hosted_zone_id}"
  name    = "${var.bastion_hostname}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_eip.master.public_ip}"]
}

resource "aws_route53_record" "api" {
  zone_id = "${var.route53_hosted_zone_id}"
  name    = "${var.openshift_public_hostname}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_eip.master.public_ip}"]
}

resource "aws_route53_record" "api_internal" {
  zone_id = "${var.route53_hosted_zone_id}"
  name    = "${var.openshift_internal_hostname}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_eip.master.public_ip}"]
}

resource "aws_route53_record" "app" {
  zone_id = "${var.route53_hosted_zone_id}"
  name    = "${var.openshift_apps_subdomain}"
  type    = "A"
  ttl     = "300"
  records = ["${aws_eip.infra.public_ip}"]
}
