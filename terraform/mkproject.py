#!/usr/bin/env python

'''
Usage:     
    mkproject.py --project=<project_name> -o <output_terraform_file>

Options:
    -o --output
'''


import os
from collections import namedtuple
from cmd import Cmd
from contextlib import ContextDecorator
import jinja2
import docopt
from snap import common
from snap import cli_tools as cli


PROJECT_VAR_NAMES = [
    'project_name',
    'ingest_bucket_name',
    'elasticsearch_cluster_size',
    'couchbase_cluster_size'
]

PROJECT_VAR_TEMPLATE = '''
{% for project_var in project_vars %}
variable "{{project_var.name}}" {
        default = "{{project_var.value}}"
}
{% endfor %}

variable "region" {
        default = "us-east-1"
}

variable "credentials_file" {
        default = "~/.ssh/aws_credentials"
}

variable "profile" {
        default = "terraform"
}
'''

TerraformVarSpec = namedtuple('TerraformVarSpec', 'name value')

class MakeProjectCLI(Cmd):
    def __init__(self, app_name='mkproject', **kwargs):
        kwreader = common.KeywordArgReader('project_name', 'output_file')
        kwreader.read(**kwargs)
        self.name = app_name
        self.project_name = kwreader.get_value('project_name')
        self.output_file = kwreader.get_value('output_file')
        self.project_var_specs = []
        self.project_var_specs.append(TerraformVarSpec(name='project_name',
                                                       value=self.project_name))

        Cmd.__init__(self)
        self.prompt = '%s [%s] > ' % (self.name, self.project_name)
        _ = os.system('clear')
        

    def get_bucket_name(self):
        should_create = cli.InputPrompt('Create S3 bucket for file ingest (Y/n)?', 'y').show()
        if should_create == 'n':
            return None
        bucket_name = cli.InputPrompt('Ingest bucket name').show()
        return bucket_name


    def get_es_cluster_size(self):
        should_create = cli.InputPrompt('Create Elasticsearch cluster (Y/n)?', 'y').show()
        if should_create == 'n':
            return 0
        cluster_size = cli.InputPrompt('Please enter the desired Elasticsearch cluster size').show()
        return int(cluster_size)


    def get_couchbase_cluster_size(self):
        should_create = cli.InputPrompt('Create Couchbase cluster (Y/n)?', 'y').show()
        if should_create == 'n':
            return 0
        cluster_size = cli.InputPrompt('Please enter the desired Couchbase cluster size').show()
        return int(cluster_size)

    
    def do_setup(self, cmd_args):
        '''Creates the required settings for Terraforming a pipeline project.
        '''
        
        ingest_bucket_name = self.get_bucket_name()
        if ingest_bucket_name:
            self.project_var_specs.append(TerraformVarSpec(name='ingest_bucket_name',
                                                           value=ingest_bucket_name))
        
        es_cluster_size = self.get_es_cluster_size()
        self.project_var_specs.append(TerraformVarSpec(name='elasticsearch_cluster_size',
                                                       value=es_cluster_size))
        
        cb_cluster_size = self.get_couchbase_cluster_size()
        self.project_var_specs.append(TerraformVarSpec(name='couchbase_cluster_size',
                                                       value=cb_cluster_size))

        print('+++ Project "%s" config vars created.' % self.project_name)


    def do_save(self, cmd_args):
        '''Saves the current configuration to the designated output file.
        '''
        
        if os.path.isfile(self.output_file):
            prompt_text = 'output file "%s" already exists. Overwrite (Y/n)?' % self.output_file
            should_overwrite = cli.InputPrompt(prompt_text, 'y').show()
            if should_overwrite == 'n':
                return

        j2env = jinja2.Environment()
        template_mgr = common.JinjaTemplateManager(j2env)        
        var_template = j2env.from_string(PROJECT_VAR_TEMPLATE)
        output_data = var_template.render(project_vars=self.project_var_specs)

        with open(self.output_file, 'w') as f:
            f.write(output_data)

        print('\n+++ Terraform project vars written to %s.\n' % self.output_file)

        
    def do_quit(self, cmd_args):
        '''Exits the mkstream environment'''
        raise SystemExit

    
    def do_q(self, cmd_args):
        '''Exits the mkstream environment'''
        self.do_quit(cmd_args)
        
        
def main(args):
    #print(common.jsonpretty(args))
    prompt = MakeProjectCLI('mkproject',
                           project_name=args['--project'],
                           output_file=args['<output_terraform_file>'])
    prompt.cmdloop('''Welcome to the mkproject interactive shell.
    Type "setup" to set project variables.
    Type help or ? to list commands.''')
    


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)


