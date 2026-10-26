.PHONY: install clean requirements test retest coverage tox lint ruff mypy format prettier sandbox test_sandbox run_test_sandbox bundle watch build

# Runs commands in the uv-managed .venv without needing to activate it.
RUN = uv run

default: install

install: clean requirements bundle

clean:
	find src -name '*.pyc' -delete
	find tests -name '*.pyc' -delete
	find . -name '*.egg-info' |xargs rm -rf

requirements:
	yarn install
	uv sync

test:
	$(RUN) pytest --nomigrations --reuse-db tests/

retest:
	$(RUN) pytest --nomigrations --reuse-db tests/ -vvv

coverage:
	$(RUN) pytest --nomigrations --reuse-db tests/ --cov=wagtail_tag_manager --cov-report=term-missing --cov-report=html

tox:
	uvx --with tox-uv tox

lint: ruff mypy

ruff:
	$(RUN) ruff format --check src tests
	$(RUN) ruff check src tests

mypy:
	$(RUN) --with mypy mypy src/ tests/

format: prettier
	$(RUN) ruff check --fix src tests
	$(RUN) ruff format src tests

prettier:
	yarn install
	yarn format

sandbox: requirements bundle
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
	$(RUN) sandbox/manage.py runserver --verbosity 0 > /dev/null 2>&1

bundle: prettier
	yarn install --force
	yarn build

watch:
	yarn dev
	yarn watch

build:
	uv build
