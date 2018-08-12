
variable "project_name" {}

variable "machine_name" {}

variable "ssh_keyname" {}

variable "ingest_bucket_name" {}

variable "elasticsearch_cluster_size" {}

variable "couchbase_cluster_size" {}

variable "region" {
	 default = "us-east-1"
}

variable "credentials_file" {
         default = "~/.ssh/aws_credentials"
}

variable "profile" {
         default = "terraform"
}


provider "aws" {
  region                  = "${var.region}"
  shared_credentials_file = "${var.credentials_file}"
  profile                 = "${var.profile}"
}


resource "aws_kms_key" "master" {
  description = "Key for encrypting S3 bucket objects"
  deletion_window_in_days = 10
}


resource "aws_key_pair" "instance_key" {
  # we provide the keyset as a variable, so that we can perform different operations
  # using different credentials if necessary
  #
  key_name = "keypair_1" 
  public_key = "${lookup(var.keyring, var.ssh_keyname)}"
}


resource "aws_s3_bucket" "ingest_bucket" {
  bucket = "${var.ingest_bucket_name}"
  acl = "authenticated-read"
}

/*
resource "aws_s3_bucket" "encrypted_ingest_bucket" {
  bucket = "${var.ingest_bucket_name}"
  acl = "authenticated-read"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        kms_master_key_id = "${aws_kms_key.master.arn}"
        sse_algorithm = "aws.kms"
      }
    }
  }
}
*/

resource "aws_instance" "elasticsearch_cluster" {
  count = "${var.elasticsearch_cluster_size}"
  base_name = "mx_elasticsearch_apollo"  # TODO: factor out the project name
  ami = "${lookup(var.amis, "elasticsearch")}"
  instance_type = "${lookup(var.instance_types, "elasticsearch")}"
  tags {
    Name = "${base_name}_${count.index}"
  }
  key_name = "keypair_1"
}


resource "aws_instance" "couchbase_cluster" {
  count = "${var.couchbase_cluster_size}"
  base_name = "mx_couchbase_apollo"   # TODO: factor out the project name
  ami = "${lookup(var.amis, "elasticsearch")}"
  instance_type = "${lookup(var.instance_types, "couchbase")}"
  tags {
    Name = "${base_name}_${count.index}"
  }
  key_name = "keypair_1"


}