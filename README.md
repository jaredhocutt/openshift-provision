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

## Provisioners

### AWS

#### Step 1

There are several variables that you will need to define before running the
AWS provisioner.

| Variable                 | Required           | Default     | Description                                                                                                                                                 |
| ------------------------ | ------------------ | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cluster_name`           | :heavy_check_mark: | `openshift` | The name of the cluster.<br><br>This value will be in your DNS entries and should conform to valid DNS characters.                                          |
| `openshift_version`      | :heavy_check_mark: | `3.9`       | The OpenShift version to install                                                                                                                            |
| `openshift_base_domain`  | :heavy_check_mark: |             | The base subdomain to use for your cluster.<br><br>Example: If you set this to `example.com`, a DNS entry for `<cluster_name>.example.com` will be created) |
| `cert_email_address`     | :heavy_check_mark: |             | The email address to use when generating Lets Encrypt certs for the cluster.                                                                                |
| `aws_region`             | :heavy_check_mark: |             | The AWS region (i.e. `us-east-1`)                                                                                                                           |
| `ec2_ami_type`           | :heavy_check_mark: | `hourly`    | If you have Cloud Access setup for your account, set this to `cloud_access`. Otherwise, set this to `hourly`.                                               |
| `route53_hosted_zone_id` | :heavy_check_mark: |             | The ID of the Route53 hosted zone (i.e. `YP563J79RELJ4C`)                                                                                                   |
| `rhsm_username`          | :heavy_check_mark: |             | Your RHSM username                                                                                                                                          |
| `rhsm_password`          | :heavy_check_mark: |             | Your RHSM password                                                                                                                                          |
| `rhsm_pool`              | :heavy_check_mark: |             | The RHSM pool ID that contains OpenShift subscriptions                                                                                                      |

For your convenience, there is an example variables file at
`<openshift-provision>/vars/aws.example.yml`. Go ahead and make a copy of this
file and update the variable values. The contents of that file is also shown below.

This guide will assume the file is located at `<openshift-provision>/vars/aws.yml`.

```yaml
---

# The name of the cluster.
# This value will be in your DNS entries and should conform to valid DNS characters.
cluster_name: openshift

# The OpenShift version to install
openshift_version: 3.9
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
```

#### Step 2

You will also need to set a few environment variables. For your convenience,
there is an example environment file at `<openshift-provision>/vars/aws.example.env`.
Go ahead and make a copy of this file and update the environment variable values. The
contents of that file is also shown below.

This guide will assume the file is located at `<openshift-provision>/vars/aws.env`.

```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
```

#### Step 3

Now you're ready to provision an OpenShift cluster in AWS.

```bash
sudo ./op.py --env-file vars/aws.env --vars-file vars/aws.yml provision
```

After your environment is provisioned, you can start and stop it by:

```bash
# Start cluster
sudo ./op.py --env-file vars/aws.env --vars-file vars/aws.yml start
# Stop cluster
sudo ./op.py --env-file vars/aws.env --vars-file vars/aws.yml stop
```

Once you no longer need your environment, you can tear it down by:

```bash
sudo ./op.py --env-file vars/aws.env --vars-file vars/aws.yml teardown
```
