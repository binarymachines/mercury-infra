#!/usr/bin/env python

'''
Usage:     
    cstream.py 

Options:
    -t --type
    -l --list
    -g --generate
'''


import os
from collections import namedtuple
import jinja2
import docopt
from snap import common


KINESIS_STREAM_TEMPLATE = '''
resource "aws_kinesis_stream" "{{ stream.tf_resource_name }}" {
  name = "{{ stream.name }}"
  shard_count = {{ stream.shard_count }}
  retention_period = {{ stream.retention_period_hours }}
  shard_level_metrics = [
    {{ stream.formatted_shard_metrics_list }}
  ]
  stream_level_metrics = [
      {{ stream.compiled_stream_metrics_list }}
  ]
}
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



