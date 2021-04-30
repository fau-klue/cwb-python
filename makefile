.PHONY: build
install:
	pipenv install --dev
test:
	pipenv run pytest -v
lint:
	pipenv run pylint --rcfile=.pylintrc cwb/*.py
coverage:
	pipenv run pytest --cov-report term-missing -v --cov=cwb/
compile:
	pipenv run cython -2 cwb/cl.pyx
build:
	pipenv run python3 setup.py build_ext --inplace
dist:
	pipenv run python3 setup.py sdist
clean:
	rm -rf *.egg-info build dist/ cwb/*.so doc/_build/
