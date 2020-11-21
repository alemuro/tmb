SHELL := /bin/bash

build: dist

.ONESHELL:
dist: virtualenv
	source virtualenv/bin/activate
	python setup.py sdist bdist_wheel

.ONESHELL:
publish: dist
	source virtualenv/bin/activate
	pip install twine
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

.ONESHELL:
publish-live: dist
	source virtualenv/bin/activate
	pip install twine
	twine upload dist/*

clean:
	rm -rf virtualenv dist build tmb.egg-info tmb/*.pyc **/__pycache__

.ONESHELL:
virtualenv: 
	virtualenv virtualenv --python=python3
	source virtualenv/bin/activate
	pip install -r requirements.txt

.ONESHELL:
test: virtualenv
	source virtualenv/bin/activate
	python -m unittest tmb