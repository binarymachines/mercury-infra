#!/usr/bin/env python


import os
import json
from collections import namedtuple
from snap import common
from snap import cli_tools as cli
from cli import mandatory_input


CouchbaseBucketSpec = namedtuple('CouchbaseBucketSpec', 'name ram_quota num_replicas')



class MakeClusterCLI(Cmd):
	def __init__(self, app_name='mkcluster', **kwargs):
		Cmd.__init__(self)
		self.prompt = '%s [%s] > ' % (self.name, self.project_name)
		_ = os.system('clear')


	def get_admin_username(self):
		with mandatory_input(cli.InputPrompt('admin username'),
				     max_retries=1,
				     warning_message='you must provide the admin user name for the cluster',
				     failure_message=abort_message) as input_result:
		return input_result.data


	def create_bucket(self):
		with mandatory_input()

	def do_new(self, cmd_args):
		admin_username = self.get_admin_username()
		admin_password = self.get_admin_password()
		cluster_ram_quota = self.get_cluster_ram_quota()

		buckets = []
		while True:
			bucket_spec = self.create_bucket()
			if bucket_spec:
				buckets.append(bucket_spec)
			else:
				print('No bucket created.')
			if not len(buckets):
				print('A working couchbase cluster must have at least one bucket.')
				print('')

	def do_save(self, cmd_args):
		pass


def main():
	



if __name__ == '__main__':
	main()


