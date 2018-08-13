HOST=127.0.0.1
TEST_PATH=./tests
RECIPEPREFIX= # prefix char is a space, on purpose; do not delete
PHONY=clean



clean: 
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +


clean-project:
	find . -name 'project_*.tf' -exec rm -f {} +	


install-deps:
	pipenv install


project:
	pipenv run ./mkproject.py --project=apollo -o project_settings.tf


credentials:
	pipenv run ./credit.py -t ssh --dir=~/.ssh -g > project_credentials.tf


streams:
	pipenv run ./mkstream.py --project=apollo -o project_streams.tf


pipeline: credentials project streams
	terraform validate
	terraform plan
