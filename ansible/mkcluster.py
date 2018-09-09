#!/usr/bin/env python


import os
import json
import re
from collections import namedtuple
from contextlib import ContextDecorator
from snap import common
from snap import cli_tools as cli
from cmd import Cmd

INT_REGEX = r'[0-9]+$'


class constrained_input_value(ContextDecorator):
    def __init__(self, value_predicate_func, cli_prompt, **kwargs):
        kwreader = common.KeywordArgReader('warning_message', 'failure_message')
        kwreader.read(**kwargs)
        
        warning_message = kwreader.get_value('warning_message')
        failure_message = kwreader.get_value('failure_message')
        
        max_retries = 1
        num_retries = 0
        self.data = cli_prompt.show()
        
        while num_retries < max_retries and not value_predicate_func(self.data):
            print('\n%s\n' % warning_message)
            self.data = cli_prompt.show()
            num_retries += 1
        
        if not self.data:
            raise Exception(failure_message)
            
    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        return False


class required_input_format(ContextDecorator):
    def __init__(self, regex_string, cli_prompt, **kwargs):
        kwreader = common.KeywordArgReader('warning_message', 'failure_message')
        kwreader.read(**kwargs)
        
        warning_message = kwreader.get_value('warning_message')
        failure_message = kwreader.get_value('failure_message')
        
        max_retries = 1
        num_retries = 0

        rx = re.compile(regex_string)
        self.data = cli_prompt.show()
        while num_retries < max_retries and not rx.match(self.data):
            print('\n%s\n' % warning_message)
            self.data = cli_prompt.show()
            num_retries += 1
        
        if not self.data:
            raise Exception(failure_message)
            
    def __enter__(self):
        return self
    
    def __exit__(self, *exc):
        return False


class mandatory_input(ContextDecorator):
    def __init__(self, cli_prompt, **kwargs):
        kwreader = common.KeywordArgReader('warning_message', 'failure_message')
        kwreader.read(**kwargs)

        warning_message = kwreader.get_value('warning_message')
        failure_message = kwreader.get_value('failure_message')
        
        max_retries = 1
        num_retries = 0
        self.data = cli_prompt.show()
        while num_retries < max_retries and not self.data:            
            print('\n%s\n' % warning_message)
            self.data = cli_prompt.show()
            num_retries += 1
        
        if not self.data:
            raise Exception(failure_message)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False



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
        self.name = app_name
        self.prompt = '%s > ' % (self.name)
        self.cluster_config = {
			'buckets': []
		}
        _ = os.system('clear')


    def get_admin_username(self):
        with mandatory_input(cli.InputPrompt('admin username'),
                     max_retries=1,
                     warning_message='you must provide the admin user name for the cluster',
                     failure_message='cannot create a cluster without a valid name') as input_result:
            return input_result.data


    def get_admin_password(self):
        with mandatory_input(cli.InputPrompt('admin password'),
                             warning_message='you must provide an admin password',
                             failure_message='no admin password provided.') as input_result:
            return input_result.data


    def get_cluster_ram_quota(self):
        with required_input_format(INT_REGEX,
                                   cli.InputPrompt('cluster RAM quota'),
                                   warning_message='cluster RAM quota must be an integer',
                                   failure_message='bad or missing cluster RAM quota') as input_result:
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
        
        value_test_func = lambda x: re.compile(INT_REGEX).match(x) and int(x) < 5
        with constrained_input_value(value_test_func,
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

		self.cluster_config['admin_username'] = admin_username
		self.cluster_config['admin_password'] = admin_password
		self.cluster_config['cluster_ram_quota'] = cluster_ram_quota

		print('\n+++ Couchbase cluster settings specified.\n')
        buckets = []

		should_add = cli.InputPrompt('Add bucket to cluster spec (Y/n)?').show()
		if should_add == 'n':
			return

        while True:
            bucket_spec = self.create_bucket()
            if bucket_spec:
                self.cluster_config['buckets'].append(bucket_spec)
                print('\n+++added bucket "%s" to cluster config\n' % bucket_spec.name)
                        
            should_continue = cli.InputPrompt('Create another bucket (Y/n)?', 'y').show()
            if should_continue == 'n':
                break

    
    def do_save(self, cmd_args):
        if not len(self.cluster_config['buckets']):
            print('A working couchbase cluster must have at least one bucket.')
            should_create = cli.InputPrompt('Create bucket (Y/n?', 'y').show()
            if should_create == 'y':
                bucket_spec = self.c



def main():
    cli_app = MakeClusterCLI()
    cli_app.cmdloop('''Welcome to the mkcluster interactive shell.
    Type "new" to provision a new Couchbase cluster against a virgin instance.
    Type "help" or "?" to list commands.''')


if __name__ == '__main__':
    main()


