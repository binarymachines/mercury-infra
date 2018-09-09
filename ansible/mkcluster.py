#!/usr/bin/env python


import os
import json
from collections import namedtuple
from snap import common
from snap import cli_tools as cli
from cli import mandatory_input


CouchbaseBucketSpec = namedtuple('CouchbaseBucketSpec', 'name type ram_quota num_replicas')

BUCKET_TYPE_OPTIONS = [
	{'label': 'couchbase', 'value': 'couchbase'},
	{'label': 'memcache', 'value': 'memcache'}
]
	

class MissingInput(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)



class MakeClusterCLI(Cmd):
	def __init__(self, app_name='mkcluster', **kwargs):
		Cmd.__init__(self)
		self.prompt = '%s [%s] > ' % (self.name, self.project_name)
		self.cluster_config = {}
		_ = os.system('clear')


	def get_admin_username(self):
		with mandatory_input(cli.InputPrompt('admin username'),
				     max_retries=1,
				     warning_message='you must provide the admin user name for the cluster',
				     failure_message=abort_message) as input_result:
		return input_result.data


	def create_bucket(self):
		bucket_name = None
		quota = None
		num_replicas = None

		with mandatory_input(cli.InputPrompt('bucket name'),						
							 warning_message='a bucket must have a name',
							 failure_message='bad or missing bucket name') as input_result:
			bucket_name = input_result.data

		bucket_type = cli.MenuPrompt('bucket type', BUCKET_TYPE_OPTIONS).show()

		with required_input_format(INT_REGEX,
								   cli.InputPrompt('bucket RAM quota'),
								   warning_message='RAM quota must be a positive integer',
								   failure_message='bad RAM quota value') as input_result:
			quota = input_result.data
		
		value_test = lambda x: x < 5
		with constrained_input_value(value_test,
									 cli.InputPrompt('number of replicas'),
									 warning_message='# of replicas must be less than 5',
									 failure_message='# of replicas outside of allowed limits') as input_result:
			num_replicas = input_result.data									

		return CouchbaseBucketSpec(name=bucket_name,
								   type=bucket_type,
								   ram_quota=quota,
								   num_replicas=num_replicas)
		

	def do_new(self, cmd_args):
		admin_username = self.get_admin_username()
		admin_password = self.get_admin_password()
		cluster_ram_quota = self.get_cluster_ram_quota()

		buckets = []
		while True:
			bucket_spec = self.create_bucket()
			if bucket_spec:
				buckets.append(bucket_spec)
				print('added bucket specification')
			else:
				print('No bucket created.')
			if len(buckets):
				should_continue = cli.InputPrompt('Create another bucket (Y/n)?', 'y').show()
				if should_continue == 'n':
					break

			else:
				print('A working couchbase cluster must have at least one bucket.')
				should_create = cli.InputPrompt('Create bucket (Y/n?', 'y').show()
				if should_create == 'n':
					break
			

		if not len(buckets):
			print('no cluster config created.')
		else:
			self.cluster_config = {
				'admin_username': admin_username,
				'admin_password': admin_password,
				'cluster_ram_quota': cluster_ram_quota,
				'buckets': buckets 
			}

			print('created cluster config:')
			print(common.jsonpretty(self.cluster_config))


		
	def do_save(self, cmd_args):
		pass


def main():
	cli_app = MakeClusterCLI()
	cli_app.cmdloop('''Welcome to the mkcluster interactive shell.
	Type "new" to provision a new Couchbase cluster against a virgin instance.
	Type "help" or "?" to list commands.''')


if __name__ == '__main__':
	main()


