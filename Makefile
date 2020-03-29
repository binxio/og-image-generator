include Makefile.mk

NAME=binx-og-image-generator

help:           ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | grep -v fgrep | sed -e 's/\([^:]*\):[^#]*##\(.*\)/printf '"'%-20s - %s\\\\n' '\1' '\2'"'/' |bash

pre-build:
	pipenv run python setup.py check
	pipenv run python setup.py build

upload-dist:		## to pypi
	rm -rf dist/*
	pipenv run python setup.py sdist
	pipenv run twine upload dist/*

clean:		## all intermediate files
	rm -rf target
	find . -name \*.pyc | xargs rm 
	find src -type d -name \*.egg-info | xargs rm -rf

test:			## run unit tests
	pipenv sync -d
	for i in $$PWD/cloudformation/*; do \
		aws cloudformation validate-template --template-body file://$$i > /dev/null || exit 1; \
	done
	PYTHONPATH=$(PWD)/src pipenv run pytest tests/test*.py

fmt:			## sources using black
	black $(find src -name *.py) tests/*.py

deploy-pipeline:				## to your AWS account
		aws cloudformation deploy \
		--capabilities CAPABILITY_IAM \
                --stack-name $(NAME)-pipeline \
                --template-file ./cloudformation/cicd-pipeline.yaml \
                --parameter-overrides \
                        S3BucketPrefix=$(S3_BUCKET_PREFIX)

delete-pipeline:				## from your AWS account
	aws cloudformation delete-stack --stack-name $(NAME)-pipeline
	aws cloudformation wait stack-delete-complete  --stack-name $(NAME)-pipeline
