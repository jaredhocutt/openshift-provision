# OpenShift Provisioner

Provision infrastructure and install OpenShift.

The goal of this project is to support installing OpenShift across multiple
clouds and virtualization platforms.

## Getting Started

This project is built using Ansible playbooks, including the use of modules
that require additional packages to be installed in order to function.

To make the process of installing the packages and their correct versions
easier, this project takes advantage of [`pipenv`](1)

If you do not already have [`pipenv`](1) installed:

```bash
pip install --user pipenv
```

Next, you can install all of the dependencies for this project:

```bash
pipenv install
```

Then, whenever you're ready to use this project, from the root directory of the
project, you run the following to activate the environment:

```bash
pipenv shell
```

## Provisioners

### AWS

If you have not already done so, activate your `pipenv` environment:

```bash
pipenv shell
```

There are several variables that you will need to define before running the
AWS provisioner.

| Variable                 | Required           | Default     | Description                                                                                                                                                 |
| ------------------------ | ------------------ | ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `cluster_name`           | :heavy_check_mark: | `openshift` | The name of the cluster.<br><br>This value will be in your DNS entries and should conform to valid DNS characters.                                          |
| `cluster_type`           | :heavy_check_mark: | `multi`     | The type of cluster to deploy.<br><br>`aio` = 1 node (all-in-one)<br>`multi` = 1 master, 1 infra, 2 app nodes<br>`ha` = 3 master, 3 infra, 2 app nodes      |
| `aws_region`             | :heavy_check_mark: |             | The AWS region (i.e. `us-east-1`)                                                                                                                           |
| `openshift_base_domain`  | :heavy_check_mark: |             | The base subdomain to use for your cluster.<br><br>Example: If you set this to `example.com`, a DNS entry for `<cluster_name>.example.com` will be created) |
| `route53_hosted_zone_id` | :heavy_check_mark: |             | The ID of the Route53 hosted zone (i.e. `YP563J79RELJ4C`)                                                                                                   |
| `ec2_key_name`           | :heavy_check_mark: |             | The name of your EC2 key pair (create one using the AWS web console if you do not have one)                                                                 |
| `ec2_key_file`           | :heavy_check_mark: |             | The path on your local filesystem to the private key file from your EC2 key pair                                                                            |
| `rhsm_username`          | :heavy_check_mark: |             | Your RHSM username                                                                                                                                          |
| `rhsm_password`          | :heavy_check_mark: |             | Your RHSM password                                                                                                                                          |
| `rhsm_pool`              | :heavy_check_mark: |             | The RHSM pool ID that contains OpenShift subscriptions                                                                                                      |
| `ec2_ami_type`           | :heavy_check_mark: | `hourly`    | If you have Cloud Access setup for your account, set this to `cloud_access`                                                                                 |
| `openshift_version`      | :heavy_check_mark: | `3.9`       | The OpenShift version to install                                                                                                                            |

For your convenience, there is an example variables file at `vars/aws.example.yml`.
Go ahead and make a copy of this file and update the variable values. This guide will assume the file is
located at `/vars/aws.yml`.

```yaml
cluster_name: openshift
cluster_type: multi

openshift_version: 3.9
openshift_base_domain: example.com

aws_region: us-east-1

ec2_ami_type: cloud_access
ec2_key_name: myawskey
ec2_key_file: ~/.ssh/myawskey.pem

route53_hosted_zone_id: YP563J79RELJ4C

rhsm_username: foo@example.com
rhsm_password: P@55w0rD
rhsm_pool: ba4e7732f8abcdad545c7f62df736d1f
```

You will also need to set a few environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
```

Now you're ready to provision an OpenShift cluster in AWS:

```bash
ansible-playbook playbooks/aws/provision.yml -e @vars/aws.yml
```

After your environment is provisioned, you can start and stop it by:

```bash
ansible-playbook playbooks/aws/start_instances.yml -e @vars/aws.yml
ansible-playbook playbooks/aws/stop_instances.yml -e @vars/aws.yml
```

[1]: https://docs.pipenv.org/
