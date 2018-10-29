#!/usr/bin/env python

import argparse
import os
import subprocess


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUPPORTED_CONTAINER_RUNTIMES = ['podman', 'docker']


class ContainerRuntimeMissingError(Exception):
    pass


class OpenShiftProvision(object):
    def __init__(self, env_file, vars_file, no_update=False, dev=False, playbook_args=[]):
        self.env_file = env_file
        self.vars_file = vars_file
        self.no_update = no_update
        self.dev = dev
        self.playbook_args = playbook_args

        self.container_runtime = self._container_runtime()
        self.container_image = 'quay.io/jhocutt/openshift-provision'
        self.keys_dir = self._keys_dir()
        self.container_command_args = self._container_command_args()

    def _container_runtime(self):
        for runtime in SUPPORTED_CONTAINER_RUNTIMES:
            try:
                subprocess.call([runtime, '--version'],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
                return runtime
            except OSError:
                pass

        raise ContainerRuntimeMissingError()

    def _keys_dir(self):
        keys_dir = os.path.join(BASE_DIR, 'playbooks', 'aws', 'keys')

        if not os.path.exists(keys_dir):
            os.mkdir(keys_dir)

        return keys_dir

    def _container_command_args(self):
        cmd_args = [
            self.container_runtime,
            'run',
            '-it',
            '--rm',
            '--env-file', self.env_file,
            '--volume', '{}:/app_vars:z'.format(os.path.dirname(os.path.abspath(self.vars_file))),
            '--volume', '{}:/app_keys:z'.format(os.path.join(BASE_DIR, self.keys_dir)),
        ]

        if self.dev:
            cmd_args = cmd_args + [
                '--volume', '{}:/app:z'.format(BASE_DIR),
            ]

        cmd_args.append(self.container_image)

        return cmd_args

    def _pull_latest_container(self):
        if self.no_update:
            print('Skipping image update.')
            return

        subprocess.call([
            self.container_runtime,
            'pull',
            self.container_image,
        ])

    def _run_playbook_command(self, playbook):
        self._pull_latest_container()

        cmd_args = self.container_command_args + [
            'ansible-playbook',
            playbook,
            '-e', 'keys_dir=/app_keys',
            '-e', '@/app_vars/{}'.format(os.path.basename(self.vars_file)),
        ] + self.playbook_args

        subprocess.call(cmd_args)

    def provision(self):
        self._run_playbook_command('playbooks/aws/provision.yml')

    def start_instances(self):
        self._run_playbook_command('playbooks/aws/start_instances.yml')

    def stop_instances(self):
        self._run_playbook_command('playbooks/aws/stop_instances.yml')

    def teardown(self):
        self._run_playbook_command('playbooks/aws/teardown.yml')

    def create_users(self):
        self._run_playbook_command('playbooks/aws/create_users.yml')

    def shell(self):
        self._pull_latest_container()
        subprocess.call(self.container_command_args + ['bash',])

    def ssh(self):
        import yaml

        with open(self.vars_file, 'r') as f:
            vars_data = yaml.load(f)

        bastion_hostname = 'bastion.{}.{}'.format(
            vars_data['cluster_name'],
            vars_data['openshift_base_domain']
        )
        keypair_filename = '/app/playbooks/aws/keys/{}-{}.pem'.format(
            vars_data['cluster_name'],
            vars_data['openshift_base_domain'].replace('.', '-')
        )

        self._pull_latest_container()

        cmd_args = self.container_command_args + [
            'ssh',
            '-i', keypair_filename,
            '-o', 'StrictHostKeyChecking=no',
            'ec2-user@{}'.format(bastion_hostname),
        ] + self.playbook_args

        subprocess.call(cmd_args)


def check_file_exists(value):
    if not os.path.isfile(value):
        raise argparse.ArgumentTypeError('The path {} does not exist'.format(value))
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action',
                        choices=['provision',
                                 'start',
                                 'stop',
                                 'teardown',
                                 'create_users',
                                 'shell',
                                 'ssh',])
    parser.add_argument('--env-file',
                        required=True,
                        type=check_file_exists,
                        help='file of environment variables')
    parser.add_argument('--vars-file',
                        required=True,
                        type=check_file_exists,
                        help='file of ansible variables')
    parser.add_argument('--no-update',
                        action='store_true')
    parser.add_argument('--dev',
                        action='store_true')
    known_args, extra_args = parser.parse_known_args()

    if os.geteuid() != 0:
        print('This script requires root privileges.')
        exit(1)

    try:
        op = OpenShiftProvision(known_args.env_file,
                                known_args.vars_file,
                                known_args.no_update,
                                known_args.dev,
                                extra_args)
    except ContainerRuntimeMissingError:
        print('\n'.join([
            'You do not have a supported container runtime installed.',
            '',
            'This script supports the following container runtimes:',
            '\n'.join('  - {}'.format(i) for i in SUPPORTED_CONTAINER_RUNTIMES),
            '',
            'Please install one of those options and try again.'
        ]))

    if known_args.action == 'provision':
        op.provision()
    elif known_args.action == 'start':
        op.start_instances()
    elif known_args.action == 'stop':
        op.stop_instances()
    elif known_args.action == 'teardown':
        op.teardown()
    elif known_args.action == 'create_users':
        op.create_users()
    elif known_args.action == 'shell':
        op.shell()
    elif known_args.action == 'ssh':
        op.ssh()
