.PHONY: install clean venv requirements test retest coverage tox lint flake8 isort mypy format black prettier sandbox test_sandbox run_test_sandbox bundle watch build

# Runs commands in the uv-managed .venv without needing to activate it.
RUN = uv run --no-project

default: install

install: clean requirements bundle

clean:
	find src -name '*.pyc' -delete
	find tests -name '*.pyc' -delete
	find . -name '*.egg-info' |xargs rm -rf

venv:
	test -d .venv || uv venv

requirements: venv
	yarn install
	uv pip install -e ".[test]"

test:
	$(RUN) pytest --nomigrations --reuse-db tests/

retest:
	$(RUN) pytest --nomigrations --reuse-db tests/ -vvv

coverage:
	$(RUN) pytest --nomigrations --reuse-db tests/ --cov=wagtail_tag_manager --cov-report=term-missing --cov-report=html

tox:
	uvx --with tox-uv tox

lint: flake8 isort mypy

mypy:
	uv pip install -U mypy
	$(RUN) mypy src/ tests/

flake8:
	uvx flake8 src/ tests/

isort:
	uvx isort src tests

format: black prettier

BLACK_EXCLUDE="/(\.git|\.hg|\.mypy_cache|\.tox|\.venv|_build|buck-out|build|dist|migrations)/"

black: isort
	uvx black --target-version py310 --verbose --exclude $(BLACK_EXCLUDE) ./src
	uvx black --target-version py310 --verbose --exclude $(BLACK_EXCLUDE) ./tests

prettier:
	yarn install
	yarn format

sandbox: bundle
	uv pip install -U -r sandbox/requirements.txt
	rm -rf db.sqlite3
	$(RUN) sandbox/manage.py migrate
	$(RUN) sandbox/manage.py loaddata sandbox/exampledata/users.json
	$(RUN) sandbox/manage.py loaddata sandbox/exampledata/cms.json
	$(RUN) sandbox/manage.py loaddata sandbox/exampledata/default_tags.json
	$(RUN) sandbox/manage.py loaddata sandbox/exampledata/additional_tags.json
	$(RUN) sandbox/manage.py runserver

test_sandbox:
	uv pip install -U -r sandbox/requirements.txt
	rm -rf db.sqlite3
	$(RUN) sandbox/manage.py migrate
	$(RUN) sandbox/manage.py loaddata sandbox/exampledata/users.json
	$(RUN) sandbox/manage.py loaddata sandbox/exampledata/cms.json
	$(RUN) sandbox/manage.py loaddata sandbox/exampledata/default_tags.json
	ENVIRONMENT=test $(RUN) sandbox/manage.py runserver --verbosity 0

run_test_sandbox:
	sandbox/manage.py runserver --verbosity 0 > /dev/null 2>&1

bundle: prettier
	yarn install --force
	yarn build

watch:
	yarn dev
	yarn watch

build:
	uv build
