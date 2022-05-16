include Makefile.mk

NAME=binx-og-image-generator

help:           ## Show this help.
	@fgrep -h "##" $(MAKEFILE_LIST) | grep -v fgrep | sed -e 's/\([^:]*\):[^#]*##\(.*\)/printf '"'%-20s - %s\\\\n' '\1' '\2'"'/' |bash

pre-build:
	rm -rf build/*
	find src -type d -name \*.egg-info | xargs rm -rf
	pipenv run python setup.py check
	pipenv run python setup.py build

.PHONY: upload-dist dist pre-build clean test

dist: pre-build		## create package for upload
	rm -rf dist/*
	pipenv run python setup.py sdist

upload-dist: dist		## to pypi
	pipenv run twine upload dist/*

clean:		## all intermediate files
	rm -rf target build/* dist/*
	find . -name \*.pyc | xargs rm 
	find src -type d -name \*.egg-info | xargs rm -rf

test:			## run unit tests
	PYTHONPATH=$(PWD)/src pipenv run pytest tests/test*.py

fmt:			## sources using black
	black $(find src -name *.py) tests/*.py

