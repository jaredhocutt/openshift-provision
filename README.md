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

### Build The Container

In order to use the container image, you first need to build it on the machine
you are going to do the install from.

This is as easy as running the following command. Replace `podman` in the
command below with `docker` if that is what you have installed on your machine instead.

```bash
sudo podman build --tag openshift-provision .
```

## Provisioners

### AWS

#### Step 1

There are several variables that you will need to define before running the
AWS provisioner.

| Variable                 | Required           | Default     | Description                                                                                                                                                 |
| ------------------------ | ------------------ | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cluster_name`           | :heavy_check_mark: | `openshift` | The name of the cluster.<br><br>This value will be in your DNS entries and should conform to valid DNS characters.                                          |
| `cluster_type`           | :heavy_check_mark: | `multi`     | The type of cluster to deploy.<br><br>`aio` = 1 node (all-in-one)<br>`multi` = 1 master, 1 infra, 2 app nodes<br>`ha` = 3 master, 3 infra, 2 app nodes      |
| `openshift_version`      | :heavy_check_mark: | `3.9`       | The OpenShift version to install                                                                                                                            |
| `openshift_base_domain`  | :heavy_check_mark: |             | The base subdomain to use for your cluster.<br><br>Example: If you set this to `example.com`, a DNS entry for `<cluster_name>.example.com` will be created) |
| `cert_email_address`     | :heavy_check_mark: |             | The email address to use when generating Lets Encrypt certs for the cluster.                                                                                |
| `aws_region`             | :heavy_check_mark: |             | The AWS region (i.e. `us-east-1`)                                                                                                                           |
| `ec2_ami_type`           | :heavy_check_mark: | `hourly`    | If you have Cloud Access setup for your account, set this to `cloud_access`                                                                                 |
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

cluster_name: openshift
cluster_type: multi

openshift_version: 3.9
openshift_base_domain: example.com

cert_email_address: foo@example.com

aws_region: us-east-1
ec2_ami_type: cloud_access
route53_hosted_zone_id: YP563J79RELJ4C

rhsm_username: foo@example.com
rhsm_password: P@55w0rD
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

Replace `podman` in the command below with `docker` if that is what you have
installed on your machine instead.

```bash
sudo podman run -it --rm --user $(id -u $USER) --volume $(pwd):/app:z --env-file vars/aws.env openshift-provision ansible-playbook playbooks/aws/provision.yml -e @vars/aws.yml -v
```

After your environment is provisioned, you can start and stop it by:

```bash
# Start cluster
sudo podman run -it --rm --user $(id -u $USER) --volume $(pwd):/app:z --env-file vars/aws.env openshift-provision ansible-playbook playbooks/aws/start_instances.yml -e @vars/aws.yml
# Stop cluster
sudo podman run -it --rm --user $(id -u $USER) --volume $(pwd):/app:z --env-file vars/aws.env openshift-provision ansible-playbook playbooks/aws/stop_instances.yml -e @vars/aws.yml
```
