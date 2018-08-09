variable "region" {
	 default = "us-east-1"
}

variable "credentials_file" {
	 default = "~/.aws/credentials"
}

variable "ami" {
	 default = "ami-759bc50a"
}

variable "profile" {
	 default = "terraform"
}


provider "aws" {
  region                  = "${var.region}"
  shared_credentials_file = "${var.credentials_file}"
  profile                 = "${var.profile}"
}

resource "aws_key_pair" "sample_ec2_key" {
  key_name = "sample_ec2_key"
  public_key = "${file("sample_ec2_key.pub")}"
}

resource "aws_instance" "web" {
  ami = "${var.ami}"
  instance_type = "t1.micro"
  tags {
    Name = "binary_terraform_test_ssh_key"
  }
  key_name = "sample_ec2_key"
}

