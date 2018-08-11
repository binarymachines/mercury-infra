#!/usr/bin/env python

'''
Usage:     
    mkstream.py -o <output_terraform_file>

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


KINESIS_STREAM_TEMPLATE = '''
{% for stream in streams %}
resource "aws_kinesis_stream" "{{ stream.tf_resource_name }}" {
  name = "{{ stream.name }}"
  shard_count = {{ stream.shard_count }}
  retention_period = {{ stream.retention_period_hours }}

  tags {
      Name = "{{ stream.name }}"
  }

  shard_level_metrics = [
    {{ stream.formatted_shard_metrics_list }}
  ]
  stream_level_metrics = [
      {{ stream.formatted_stream_metrics_list }}
  ]
}

{% endfor %}
'''


class StreamSpec(object):
    def __init__(self, stream_name, terraform_resource_name, shard_count, retention_hrs=24):
        self.name = stream_name
        self.tf_resource_name = terraform_resource_name
        self.shard_count = int(shard_count)
        self.retention_period_hours = int(retention_hrs)
        self.stream_metrics = []
        self.shard_metrics = []


    def add_shard_metric(self, metric_name):
        self.shard_metrics.append(metric_name)

    def add_stream_metric(self, metric_name):
        self.stream_metrics.append(metric_name)

    @property
    def compiled_shard_metrics_list(self):
        return ',\n'.join(self.shard_metrics)

    @property
    def compiled_stream_metrics_list(self):
        return ',\n'.join(self.stream_metrics)


def docopt_cmd(func):
    """
    This decorator is used to simplify the try/except block and pass the result
    of the docopt parsing to the called action.
    """
    def fn(self, arg):
        try:
            opt = docopt_func(fn.__doc__, arg)

        except DocoptExit as e:
            # The DocoptExit is thrown when the args do not match.
            # We print a message to the user and the usage block.

            print('\nPlease specify one or more valid command parameters.')
            print(e)
            return

        except SystemExit:
            # The SystemExit exception prints the usage for --help
            # We do not need to do the print here.

            return

        return func(self, opt)

    fn.__name__ = func.__name__
    fn.__doc__ = func.__doc__
    fn.__dict__.update(func.__dict__)
    return fn


class MissingInput(Exception):
    def __init__(self, message):
        Exception.__init__(self, message)


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
            raise MissingInputException(failure_message)


    def __enter__(self):
        return self


    def __exit__(self, *exc):
        return False


class MakeStreamCLI(Cmd):
    def __init__(self, app_name='mkstream', **kwargs):
        kwreader = common.KeywordArgReader('output_file')
        kwreader.read(**kwargs)
        self.output_file = kwreader.get_value('output_file')
        self.name = app_name
        Cmd.__init__(self)
        self.prompt = '%s> ' % self.name
        self.stream_specs = []
        _ = os.system('clear')


    def do_new(self, cmd_args):

        abort_message = 'cancelling stream creation.'
        try:
            stream_name = None
            resource_name = None

            with mandatory_input(cli.InputPrompt('Kinesis stream name'),
                                 max_retries=1,
                                 warning_message='a Kinesis stream requires a name.',
                                 failure_message=abort_message) as input_result:
                stream_name = input_result.data

            with mandatory_input(cli.InputPrompt('Terraform resource name'),
                                 max_retries=1,
                                 warning_message='a Kinesis stream requires a Terraform resource name.',
                                 failure_message=abort_message) as input_result:
                resource_name = input_result.data

            # TODO: add mandatory_type and mandatory_format context managers, factor into snap.cli module

            shard_count = cli.InputPrompt('shard count', '1').show()
            retention_period = cli.InputPrompt('data retention period in hours', '24').show()

            stream_spec = StreamSpec(stream_name, resource_name, shard_count, retention_period)

            self.stream_specs.append(stream_spec)


        except MissingInput as err:
            print(err.message)
            return


    def do_save(self, cmd_args):
        '''Saves all created Kinesis stream resources to the designated output .tf file.'''

        if not len(self.stream_specs):
            print('No Kinesis streams defined.')
            return

        if os.path.isfile(self.output_file):
            print('designated output file already exists.')
            return
        
        j2env = jinja2.Environment()
        template_mgr = common.JinjaTemplateManager(j2env)        
        streamdef_template = j2env.from_string(KINESIS_STREAM_TEMPLATE)
        output_data = streamdef_template.render(streams=self.stream_specs)

        with open(self.output_file, 'w') as f:
            f.write(output_data)

        print('\nSaved Terraform resources to output file %s.\n' % self.output_file)


def main(args):
    #print(common.jsonpretty(args))
    prompt = MakeStreamCLI('mkstream', output_file=args['<output_terraform_file>'])
    prompt.cmdloop('starting mkstream in interactive mode...')


if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    main(args)