# mercury-infra
**Terraform and Ansible files for data pipeline infrastructure**

This repo contains:

* the Terraform files for spinning up the EC2 instances that host initial, core, and terminal pipeline datastores
* associated structures such as VPC's and security groups

_COMING SOON:_ addition of Ansible files (from the binarymachines **warp** repo) for further provisioning of required services on pipeline EC2 instances.

Overview: Pipeline structure
---------

AWS-hosted Mercury data pipelines have a defined structure, consisting of:

* an initial datastore, often in the form of an S3 bucket
* a core datastore, which may include one or more Kafka topics (or Kinesis streams), or a key-value NoSQL database such as Couchbase
* one or more terminal datastores, in which cleaned, corrected, and transformed records are deposited. These may include Elasticsearch, PostgreSQL, or any other database against which consumers of the pipeline's output intend to issue queries.

The code in mercury-infra is based on the Terraform orchestration framework, augmented by Python scripts. Its purpose is to semi-automate the process of creating the large-scale structures and security relationships required to build out a Mercury data pipeline.

Prerequisites
-------------

mercury-infra requires:

* Python 3.5 or higher
* Pipenv for dependency management
* a working Terraform install
* a valid set of AWS credentials (a secret access key and an access key ID)

mercury-infra has as yet only been tested in a UNIX environment. Behavior under the Windows Powershell is undefined.

Usage
-------------
To construct a pipeline using mercury-infra, ensure that your AWS credentials are present as environment variables. Clone the repo into a local directory, then cd into < mercury-infra directory >/terraform. Inspect the Makefile and ensure that in the credentials make target, the `--dir` paramter points to a directory housing a valid SSH keypair. (NOTE: this will be parameterized in a later build.)

Then, at the command prompt, issue

````
make pipeline
````

This will open up the `mkproject` interactive shell, in which you will input general project information and select the desired settings for clustered datastores (currently only Elasticsearch and Couchbase are supported; additional datatypes will be available in an upcoming build). 

Type `setup` and follow the prompts, then type `save` to write the generated data to a Terraform (.tf) file, and finally `quit` (or `q`) to exit.

The next interactive shell will be the `mkstream` shell, for setting up Kinesis streams. Type `new` to create a new stream, then -- as with the previous shell -- type `save` to write the configuration to a Terraform file and `q` to exit.

Upon successful termination of the setup shells, the `terraform validate` and `terraform plan` commands will automatically execute. This will generate a readout detailing the infrastructure components to be created or updated. Finally, issue `terraform apply` at the command line to execute the build plan and construct the specified resources on AWS. Upon completion of the apply command, the AWS resources will be ready for initial use (or further provisioning).

Issue `terraform destroy` to shut down and remove any AWS infrastructure generated in the previous step.


Next Steps
----------------

Ansible is a more fine-grained tool for provisioning -- among other types -- AWS resources such as EC2 instances. Future builds will integrate parameterized Ansible scripts from the *warp* repo to automate as much as possible of the pipeline setup process, enabling users to rapidly prototype and experiment with data pipelines without tedious manual setup and teardown.

Additionally, the machine types available in mercury-infra are limited to those types compatible with EC2-Classic. Support for t2 and  instance types (which require VPC provisioning), as well as non-EC2 resource types, is under development.


mercury-infra and its sister repository mercury are free and open-source software from [Binarymachines LLC](https://www.binarymachines.io).
