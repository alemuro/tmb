build: dist

dist: virtualenv
	source virtualenv/bin/activate && \
	python setup.py sdist bdist_wheel

publish: dist
	source virtualenv/bin/activate && \
	pip install twine && \
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

publish-live: dist
	source virtualenv/bin/activate && \
	pip install twine && \
	twine upload dist/*

clean:
	rm -rf virtualenv dist build tmb.egg-info tmb/*.pyc **/__pycache__

virtualenv: 
	virtualenv virtualenv --python=python3 && \
	source virtualenv/bin/activate && \
	pip install -r requirements.txt