
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

resource "aws_instance" "web" {
  ami = "${lookup(var.amis, "elasticsearch")}"
  instance_type = "t1.micro"
  tags {
    Name = "${var.machine_name}"
  }
  key_name = "keypair_1"
}

