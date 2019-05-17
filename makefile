install:
	pipenv install --dev
test:
	pipenv run pytest -v
lint:
	pipenv run pylint --rcfile=.pylintrc cwb_python/*.py
coverage:
	pipenv run pytest --cov-report term-missing -v --cov=cwb_python
compile:
	pipenv run python3 setup.py build_ext --inplace
build:
	pipenv run python3 setup.py sdist
clean:
	rm -rf *.egg-info build
