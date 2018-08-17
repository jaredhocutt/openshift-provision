#!/usr/bin/env python

import argparse
import os
import subprocess


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUPPORTED_CONTAINER_RUNTIMES = ['podman', 'docker']


class ContainerRuntimeMissingError(Exception):
    pass


class OpenShiftProvision(object):
    def __init__(self, env_file, vars_file, dev=False, playbook_args=[]):
        self.env_file = env_file
        self.vars_file = vars_file
        self.dev = dev
        self.playbook_args = playbook_args

        self.container_runtime = self._container_runtime()
        self.container_image = 'quay.io/jhocutt/openshift-provision'
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

    def _container_command_args(self):
        cmd_args = [
            self.container_runtime,
            'run',
            '-it',
            '--rm',
            '--env-file', self.env_file,
            '--volume', '{}:/app_vars:z'.format(os.path.dirname(os.path.abspath(self.vars_file))),
            '--volume', '{}:/app_keys:z'.format(os.path.join(BASE_DIR, 'keys')),
        ]

        if self.dev:
            cmd_args = cmd_args + [
                '--volume', '{}:/app:z'.format(BASE_DIR),
            ]

        cmd_args.append(self.container_image)

        return cmd_args

    def _pull_latest_container(self):
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
                                 'teardown',])
    parser.add_argument('--env-file',
                        required=True,
                        type=check_file_exists,
                        help='file of environment variables')
    parser.add_argument('--vars-file',
                        required=True,
                        type=check_file_exists,
                        help='file of ansible variables')
    parser.add_argument('--dev',
                        action='store_true')
    known_args, extra_args = parser.parse_known_args()

    if os.geteuid() != 0:
        print('This script requires root privileges.')
        exit(1)

    try:
        op = OpenShiftProvision(known_args.env_file,
                                known_args.vars_file,
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
