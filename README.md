# OpenShift Provisioner

Provision infrastructure and install OpenShift.

The goal of this project is to support installing OpenShift across multiple
clouds and virtualization platforms.

## Getting Started

This project is built using Ansible playbooks, including the use of modules
that require additional packages to be installed in order to function.

To make the use of this project easier, a container has been created that has
all of the required dependencies and is configured to work out of the box.

To use the container, you will need a container runtime. I recommend using
[podman](https://github.com/projectatomic/libpod) or
[docker](https://www.docker.com/community-edition).

## Known Issues

### Issue: Docker for Mac does not work

Running this tool using Docker for Mac does not work. During the OpenShift
installation portion, which is a long running process, the Ansible SSH
connection will drop and not recover.

This does not happen when running from a Linux machine. Therefore, the
current workaround is to use a Linux VM (either on your Mac or running
in AWS) and execute this tool from that Linux VM.

This issue will exhibit itself with an error that looks similar to the following:

```bash
TASK [install_openshift : Run OpenShift installer (this will take a while!)] **
Friday 17 August 2018 21:26:08 +0000 (0:02:35.555) 0:26:59.634 *********
fatal: [ec2-18-232-178-150.compute-1.amazonaws.com]: UNREACHABLE! => {
"changed": false,
"unreachable": true
}

MSG:

Failed to connect to the host via ssh: Shared connection to 18.232.178.150 closed.
```

## Provisioners

### AWS

#### Deploy

##### Step 1

There are several variables that you will need to define before running the
AWS provisioner.

| Variable                         | Required           | Default         | Description                                                                                                                                                                                     |
| -------------------------------- | ------------------ | --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cluster_name`                   | :heavy_check_mark: | `openshift`     | The name of the cluster.<br><br>This value will be in your DNS entries and should conform to valid DNS characters.                                                                              |
| `openshift_version`              | :heavy_check_mark: | `3.10`          | The OpenShift version to install. This tool currently supports 3.9 and 3.10.<br><br>**IMPORTANT:** Make sure this value is quoted, otherwise 3.10 gets read as 3.1 instead of 3.10.             |
| `openshift_base_domain`          | :heavy_check_mark: |                 | The base subdomain to use for your cluster.<br><br>Example: If you set this to `example.com`, a DNS entry for `<cluster_name>.example.com` will be created)                                     |
| `cert_email_address`             | :heavy_check_mark: |                 | The email address to use when generating Lets Encrypt certs for the cluster.                                                                                                                    |
| `aws_region`                     | :heavy_check_mark: |                 | The AWS region (i.e. `us-east-1`)                                                                                                                                                               |
| `ec2_ami_type`                   | :heavy_check_mark: | `hourly`        | If you have Cloud Access setup for your account, set this to `cloud_access`. Otherwise, set this to `hourly`.                                                                                   |
| `route53_hosted_zone_id`         | :heavy_check_mark: |                 | The ID of the Route53 hosted zone (i.e. `YP563J79RELJ4C`)                                                                                                                                       |
| `rhsm_username`                  | :heavy_check_mark: |                 | Your RHSM username                                                                                                                                                                              |
| `rhsm_password`                  | :heavy_check_mark: |                 | Your RHSM password                                                                                                                                                                              |
| `rhsm_pool`                      | :heavy_check_mark: |                 | The RHSM pool ID that contains OpenShift subscriptions                                                                                                                                          |
| `openshift_users`                |                    | `[]`            | A list of users to create in the OpenShift cluster.<br><br>Each item in the list should include `username`, `password`, and optionally `admin`. See the example vars file below for an example. |
| `app_node_count`                 |                    | `2`             | The number of app nodes to provision                                                                                                                                                            |
| `ec2_vpc_cidr_block`             |                    | `172.31.0.0/16` | The CIDR block for the VPC                                                                                                                                                                      |
| `ec2_instance_type_bastion`      |                    | `t2.medium`     | The EC2 instance type for the bastion node                                                                                                                                                      |
| `ec2_instance_type_master`       |                    | `m4.xlarge`     | The EC2 instance type for the master node                                                                                                                                                       |
| `ec2_instance_type_infra`        |                    | `m4.xlarge`     | The EC2 instance type for the infra node                                                                                                                                                        |
| `ec2_instance_type_app`          |                    | `m4.large`      | The EC2 instance type for the app nodes                                                                                                                                                         |
| `ec2_volume_size_bastion_root`   |                    | `10`            | The root disk size (in GB) for the bastion node                                                                                                                                                 |
| `ec2_volume_size_master_root`    |                    | `60`            | The root disk size (in GB) for the master node                                                                                                                                                  |
| `ec2_volume_size_infra_root`     |                    | `60`            | The root disk size (in GB) for the infra node                                                                                                                                                   |
| `ec2_volume_size_app_root`       |                    | `60`            | The root disk size (in GB) for the app nodes                                                                                                                                                    |
| `ec2_volume_size_cns`            |                    | `100`           | The disk size (in GB) for the CNS disk                                                                                                                                                          |
| `cns_block_host_volume_size`     |                    | `50`            | The volume size (in GB) of GlusterFS volumes that will be automatically create to host glusterblock volumes                                                                                     |
| `openshift_registry_volume_size` |                    | `20`            | The volume size (in GB) to provision for the integration OpenShift registry                                                                                                                     |

For your convenience, there is an example variables file at
`<openshift-provision>/vars/aws.example.yml`. Go ahead and make a copy of this
file and update the variable values. The contents of that file is also shown below.

This guide will assume the file is located at `<openshift-provision>/vars/aws.yml`.

```yaml
# The name of the cluster.
# This value will be in your DNS entries and should conform to valid DNS characters.
cluster_name: openshift

# The OpenShift version to install
# IMPORTANT: Make sure this value is quoted, otherwise it gets read as 3.1 instead of 3.10
openshift_version: "3.10"
# The base subdomain to use for your cluster.
# Example: If you set this to `example.com`, a DNS entry for `<cluster_name>.example.com` will be created)
openshift_base_domain: example.com

# The email address to use when generating Lets Encrypt certs for the cluster.
cert_email_address: foo@example.com

# The AWS region (i.e. `us-east-1`)
aws_region: us-east-1
# If you have Cloud Access setup for your account, set this to `cloud_access`. Otherwise, set this to `hourly`.
ec2_ami_type: cloud_access
# The ID of the Route53 hosted zone
route53_hosted_zone_id: YP563J79RELJ4C

# Your RHSM username
rhsm_username: foo@example.com
# Your RHSM password
rhsm_password: P@55w0rD
# The RHSM pool ID that contains OpenShift subscriptions
rhsm_pool: ba4e7732f8abcdad545c7f62df736d1f

# The users to create in OpenShift
openshift_users:
  - username: admin
    password: password
    admin: yes
  - username: user1
    password: password
  - username: user2
    password: password
  - username: user3
    password: password
```

##### Step 2

You will also need to set a few environment variables. For your convenience,
there is an example environment file at `<openshift-provision>/vars/aws.example.env`.
Go ahead and make a copy of this file and update the environment variable values. The
contents of that file is also shown below.

This guide will assume the file is located at `<openshift-provision>/vars/aws.env`.

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

##### Step 3

Now you're ready to provision an OpenShift cluster in AWS.

```bash
sudo ./op.py --env-file vars/aws.env --vars-file vars/aws.yml provision
```

Once the provisioning has completed successfully, you will be able to access
your cluster at `{{ cluster_name }}.{{ openshift_base_domain }}`.

For example, if you set:

```yaml
cluster_name: ocp
openshift_base_domain: mydomain.com
```

your OpenShift cluster would be accessible at `ocp.mydomain.com`.

#### Manage

##### Start / Stop

After your environment is provisioned, it's likely you'll want to shut it down
when you're not using it and be able to start it back up when you need it.

This is recommended as the compute costs for this cluster can get pricey if
left running. For example, the default cluster config would be:

- 1 t2.medium at $0.0464 per hour
- 2 m4.xlarge at $0.20 per hour
- 2 m4.large at $0.10 per hour

That comes out to a little more than $15 per day and ~$465 per month.

You can start and stop your cluster by:

```bash
# Start cluster
sudo ./op.py --env-file vars/aws.env --vars-file vars/aws.yml start
# Stop cluster
sudo ./op.py --env-file vars/aws.env --vars-file vars/aws.yml stop
```

##### Create / Update Users

If you need to add or update users in OpenShift:

```bash
sudo ./op.py --env-file vars/aws.env --vars-file vars/aws.yml create_users
```

##### Teardown

Once you no longer need your environment, you can tear it down by:

```bash
sudo ./op.py --env-file vars/aws.env --vars-file vars/aws.yml teardown
```
