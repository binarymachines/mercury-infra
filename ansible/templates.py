#!/usr/bin/env python


couchbase_setup_ansible_command = '''
---
# 
# Set up Couchbase cluster from a single command
#
     
- name: Initialize the cluster and add the nodes to the cluster
  hosts: couchbase-main
  user: root 

  tasks:
  - name: Configure main node
    shell: /opt/couchbase/bin/couchbase-cli cluster-init -c 127.0.0.1:8091  --cluster-init-username={{cluster_spec.admin_username}} --cluster-init-password={{cluster_spec.admin_password}} --cluster-init-port=8091 --cluster-init-ramsize={{cluster_spec.cluster_ram_quota}} 

  - name: Create shell script for configuring main node
    action: template src=couchbase-add-node.j2 dest=/tmp/addnodes.sh mode=750
  
  - name: Launch config script
    action: shell /tmp/addnodes.sh
  
  - name: Rebalance the cluster
    shell: /opt/couchbase/bin/couchbase-cli rebalance -c 127.0.0.1:8091 -u ${admin_user} -p ${admin_password}      

{% for bucket in cluster_spec.buckets %}
  - name: create bucket {{bucket.name}} with {{bucket.num_replicas}} replicas
    shell: /opt/couchbase/bin/couchbase-cli bucket-create -c 127.0.0.1:8091 --bucket={{bucket.name}} --bucket-type={{bucket.type}} --bucket-port=11211 --bucket-ramsize={{bucket.ram_quota}}  --bucket-replica={{bucket.num_replicas}} -u {{cluster_spec.admin_user}} -p {{cluster_spec.admin_password}}
{% endfor %}  

'''

COUCHBASE_ADD_NODE_SHELL_SCRIPT = '''
/opt/couchbase/bin/couchbase-cli server-add -c 127.0.0.1:8091 -u ${admin_user} -p ${admin_password} \
--server-add={{ node_address }}:{{ node_port }} \
--server-add-username=${admin_user} --server-add-password=${admin_password} \
--services data, index, query 
'''

COUCHBASE_SETUP_SHELL_SCRIPT = '''
#!/bin/bash

/opt/couchbase/bin/couchbase-cli cluster-init -c 127.0.0.1:8091  \
--cluster-init-username={{cluster_spec.admin_username}} \
--cluster-init-password={{cluster_spec.admin_password}} \
--cluster-init-port=8091 \
--cluster-init-ramsize={{cluster_spec.cluster_ram_quota}} 



'''