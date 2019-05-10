install:
	pipenv install --dev
test:
	pipenv run pytest -v
lint:
	pipenv run pylint --rcfile=.pylintrc py_src/*.py
coverage:
	pipenv run pytest --cov-report term-missing -v --cov=py_src/
compile:
	pipenv run python3 setup.py build_ext --inplace
build:
	pipenv run python3 setup.py sdist
clean:
	rm -rf *.egg-info build
