#!/usr/bin/env python

import argparse
import os
import subprocess


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUPPORTED_CONTAINER_RUNTIMES = ['podman', 'docker']


class ContainerRuntimeMissingError(Exception):
    pass


class OpenShiftProvision(object):
    def __init__(self, env_file, vars_file, verbosity=0):
        self.env_file = env_file
        self.vars_file = vars_file
        self.verbosity = verbosity

        self.container_runtime = self._container_runtime()
        self.container_command_args = [
            self.container_runtime,
            'run',
            '-it',
            '--rm',
            '--env-file', self.env_file,
            '--volume', '{}:/app:z'.format(BASE_DIR),
            'quay.io/jhocutt/openshift-provision',
        ]

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

    def _run_playbook_command(self, playbook):
        cmd_args = self.container_command_args + [
            'ansible-playbook',
            playbook,
            '-e', '@{}'.format(self.vars_file),
        ]

        if self.verbosity > 0:
            cmd_args.append('-{}'.format('v' * self.verbosity))

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
    parser.add_argument('-v', '--verbose',
                        action='count',
                        help='verbose mode (-vvv for more, -vvvv to enable connection debugging)')
    args = parser.parse_args()

    if os.geteuid() != 0:
        print('This script requires root privileges.')
        exit(1)

    try:
        op = OpenShiftProvision(args.env_file,
                                args.vars_file,
                                args.verbose)
    except ContainerRuntimeMissingError:
        print('\n'.join([
            'You do not have a supported container runtime installed.',
            '',
            'This script supports the following container runtimes:',
            '\n'.join('  - {}'.format(i) for i in SUPPORTED_CONTAINER_RUNTIMES),
            '',
            'Please install one of those options and try again.'
        ]))

    if args.action == 'provision':
        op.provision()
    elif args.action == 'start':
        op.start_instances()
    elif args.action == 'stop':
        op.stop_instances()
    elif args.action == 'teardown':
        op.teardown()
