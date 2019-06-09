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
compile-docker:
	bash docker-compile.sh
build:
	pipenv run python3 setup.py sdist
clean:
	rm -rf *.egg-info build/ dist/ cwb_python/CWB/*.so cwb_python/CWB/*.c cwb_python/CWB/*.h
