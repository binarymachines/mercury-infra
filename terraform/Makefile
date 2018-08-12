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
	pipenv run ./mkproject.py --name=apollo -o project_settings.tf


credentials:
	pipenv run ./credit.py -t ssh --dir=~/.ssh -g > project_credentials.tf


core:
	pipenv run ./mkstream.py --project=apollo -o project_streams.tf


pipeline: project credentials core
	echo "making a pipeline"
