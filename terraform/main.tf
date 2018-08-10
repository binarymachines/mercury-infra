
variable "machine_name" {}

variable "ssh_keyname" {}

provider "aws" {
  region                  = "${var.region}"
  shared_credentials_file = "${var.credentials_file}"
  profile                 = "${var.profile}"
}

resource "aws_key_pair" "instance_key" {
  # we provide the keyset as a variable, so that we can perform different operations
  # using different credentials if necessary
  #
  key_name = "keypair_1" 
  public_key = "${lookup(var.keyring, var.ssh_keyname)}"
}

resource "aws_instance" "elasticsearch_cluster" {
  count = "${var.elasticsearch_cluster_size}"
  base_name = "mx_elasticsearch_apollo"  # TODO: factor out the project name
  ami = "${lookup(var.amis, "elasticsearch")}"
  instance_type = "${lookup(var.instance_types. "elasticsearch")}"
  tags {
    Name = "${base_name}_${count.index}"
  }
  key_name = "keypair_1"
}

resource "aws_instance" "couchbase_cluster" {
  count = "${var.couchbase_cluster_size}"
  base_name = "mx_couchbase_apollo"   # TODO: factor out the project name
  ami = "${lookup(var.amis, "elasticsearch")}"
  instance_type = "${lookup(var.instance_types. "elasticsearch")}"
  tags {
    Name = "${base_name}_${count.index}"
  }
  key_name = "keypair_1"


}