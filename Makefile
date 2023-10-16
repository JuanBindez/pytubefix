dev:
	pipenv install --dev

pipenv:
	pip install pipenv
	pipenv install --dev

deploy-patch: clean requirements bumpversion-patch upload clean

deploy-minor: clean requirements bumpversion-minor upload clean

deploy-major: clean requirements bumpversion-major upload clean

requirements:
	pipenv_to_requirements


bump_%: VER=$(patsubst bump_%,%,$@)
bump_%: ## Bump Version with wildcard
	pipenv run bump-my-version bump ${VER}
	
push_bump:
	git push
	git push --tags

bumpversion-patch: bump_patch push_bump

bumpversion-minor: bump_minor push_bump

bumpversion-major: bump_major push_bump

git-push:
	git push -u origin main

upload:
	pip install twine build
	python -m build
	twine upload dist/*

help:
	@echo "clean - remove all build, test, coverage and Python artifacts"
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "install - install the package to the active Python's site-packages"

ci:
	pip install pipenv
	pipenv install --dev --skip-lock
	pipenv run flake8
	# pipenv run pytest --cov-report term-missing # --cov=humps
	pipenv run coverage run -m pytest

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.DS_Store' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

install: clean
	python -m pip install -e .
