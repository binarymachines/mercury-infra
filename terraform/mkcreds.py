#!/usr/bin/env python

'''
Usage:     
    mkcreds.py -t (ssh | aws) --dir=<directory> (-l | -g)

Options:
    -t --type
    -l --list
    -g --generate
'''


import os
import json
from collections import namedtuple
import jinja2
import docopt
from snap import common


KEYRING_TEMPLATE = '''
variable "keyring" {
  type = "map"
  description = "map of SSH key pairs and their locations"
  default = {
  	  {% for keypair in keypairs %}
  	  {{ keypair.name }} = "{{ keypair.public_key }}"
	  {% endfor %}
  }
}
'''


KeypairRecord = namedtuple('KeypairRecord', 'name public_key')


def find_keyfiles_in_dir(directory):    
    files = os.listdir(directory)
    return [f for f in files if f.endswith('.pub') or f.endswith('.pem')]


def load_keys(pubkey_table, directory):
    keydata = {}
    for key_label in pubkey_table:
        filepath = os.path.join(directory, pubkey_table[key_label])
        pubkey = None
        with open(filepath, 'r') as f:
            pubkey = f.read()
        keydata[key_label] = pubkey.lstrip().rstrip()
    return keydata


def main(args):
    #print(common.jsonpretty(args))

    credential_type = 'unsupported'
    if args.get('ssh'):
        credential_type = 'ssh'
    elif args.get('aws'):
        credential_type = 'aws'

    j2env = jinja2.Environment()
    template_mgr = common.JinjaTemplateManager(j2env)
    keyring_varfile_template = j2env.from_string(KEYRING_TEMPLATE)

    keyfile_dir = os.path.expanduser(args['--dir'])
    keyfiles = find_keyfiles_in_dir(keyfile_dir)

    # TODO: add an interactive portion to allow users to label keys
    key_table = {}
    index = 0
    for kfile in keyfiles:
        label = kfile[0:-4]
        key_table[label] = kfile
        index += 1

    key_data = load_keys(key_table, keyfile_dir)
    keypair_records = []
    for label, key in key_data.items():
        keypair_records.append(KeypairRecord(name=label, public_key=key))

    print(keyring_varfile_template.render(keypairs=keypair_records))

    with open('keyfiles.json', 'w') as f:
        keymap = {}
        keymap['location'] = keyfile_dir
        keymap['public_keys'] = key_data
        f.write(json.dumps(keymap))

    #print(common.jsonpretty(key_data))
                               

if __name__ == '__main__':
   args = docopt.docopt(__doc__)
   main(args)
