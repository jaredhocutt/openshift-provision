#!/usr/bin/env python3

import argparse
import logging
import os
import subprocess
import yaml

from bullet import Bullet


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PLAYBOOKS_DIR = os.path.join(BASE_DIR, 'playbooks')

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class OpenShiftDeploy(object):
    def __init__(self, vars_file, extra_args=[]):
        self.vars_file = vars_file
        self.extra_args = extra_args

        self.vars_yaml = self._vars_yaml()
        self.deployment_cloud = self.vars_yaml['deployment_cloud']
        self.deployment_type = self.vars_yaml['deployment_type']

    def provision(self):
        self._run_playbook(
            os.path.join(PLAYBOOKS_DIR, 'aws_multi_node.yml'))

    def destroy(self):
        self._run_playbook(
            os.path.join(PLAYBOOKS_DIR, 'aws_multi_node_destroy.yml'))

    def start(self):
        self._run_playbook(
            os.path.join(PLAYBOOKS_DIR, 'aws_start_instances.yml'))

    def stop(self):
        self._run_playbook(
            os.path.join(PLAYBOOKS_DIR, 'aws_stop_instances.yml'))

    def ssh(self):
        if self.deployment_cloud == 'aws':
            self._ssh_aws()

    def _run_playbook(self, playbook):
        cmd_args = [
            'ansible-playbook', playbook,
            '-e', '@{}'.format(self.vars_file)
        ]

        cmd_args = cmd_args + self.extra_args
        logger.debug(cmd_args)

        subprocess.call(cmd_args)

    def _vars_yaml(self):
        with open(self.vars_file, 'r') as f:
            y = yaml.safe_load(f)
        logger.debug(y)

        return y

    def _ssh_aws(self):
        hostname = self.vars_yaml.get(
            'bastion_hostname',
            'bastion.{}.{}'.format(
                self.vars_yaml['openshift_cluster_name'],
                self.vars_yaml['openshift_base_domain'],
            )
        )

        cmd_args = [
            'ssh',
            '-i', self.vars_yaml['aws_keypair_path'],
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            'ec2-user@{}'.format(hostname),
        ]
        logger.debug(cmd_args)

        subprocess.call(cmd_args)


class OpenShiftDeployCLI(object):
    def __init__(self):
        self.parser = argparse.ArgumentParser()
        self._add_parser_arguments()

        self.subparsers      = self.parser.add_subparsers()
        self.sp_provision    = self._add_subparser('provision')
        self.sp_destroy      = self._add_subparser('destroy')
        self.sp_start        = self._add_subparser('start')
        self.sp_stop         = self._add_subparser('stop')
        self.sp_ssh          = self._add_subparser('ssh')

        self.known_args, self.extra_args = self.parser.parse_known_args()

        self.bullet_style = {
            "align": 4,
            "indent": 0,
            "margin": 1,
            "pad_right": 2,
            "shift": 0,
            "bullet": "⮞",
        }

        self._vars_file = self.known_args.vars_file

        logger.setLevel(getattr(logging, self.known_args.loglevel.upper()))

    @staticmethod
    def check_file_exists(value):
        if not os.path.isfile(value):
            raise argparse.ArgumentTypeError(
                'The path {} does not exist'.format(value))
        return value

    def _add_subparser(self, name):
        sp = self.subparsers.add_parser(name)
        sp.set_defaults(action=name)
        return sp

    def _add_parser_arguments(self):
        self.parser.add_argument('--vars-file', type=OpenShiftDeployCLI.check_file_exists)
        self.parser.add_argument(
            '--loglevel',
            choices=[
                'DEBUG', 'debug',
                'INFO', 'info',
                'WARNING', 'warning',
                'ERROR', 'error',
                'CRITICAL', 'critical',
            ],
            default='WARNING'
        )

    @property
    def vars_file(self):
        if not self._vars_file:
            result = Bullet(
                prompt='Select a variable file to use: ',
                choices=os.listdir(os.path.join(BASE_DIR, 'vars')),
                **self.bullet_style,
            ).launch()

            self._vars_file = os.path.join(BASE_DIR, 'vars', result)

        return self._vars_file

    def run(self):
        deploy = OpenShiftDeploy(self.vars_file, self.extra_args)

        if self.known_args.action == 'provision':
            deploy.provision()
        elif self.known_args.action == 'destroy':
            deploy.destroy()
        elif self.known_args.action == 'start':
            deploy.start()
        elif self.known_args.action == 'stop':
            deploy.stop()
        elif self.known_args.action == 'ssh':
            deploy.ssh()


if __name__ == '__main__':
    cli = OpenShiftDeployCLI()
    cli.run()
