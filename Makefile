# This Makefile contains commands for managing the project's dependencies, running the server,
# building and managing Docker containers, and running tests and linters. To use this Makefile,
# run `make <target>`, where `<target>` is the name of the command you want to run.

.PHONY: install build run up-docker down-docker down-docker-v test lint lint-ci

# Install the dependencies
install:
	@poetry install
# Build docker image
build:
	@docker build -t final-pyweb-image .
# Start server directly
run:
	@poetry run uvicorn src.main:app --port 80
# Start a docker container with the server
up-docker:
	@docker-compose up -d --build
# Stop docker container and preserve volumes
down-docker:
	@docker-compose down
# Stop docker container and delete volumes
down-docker-v:
	@docker-compose down --volumes
# Run tests
test:
	@poetry run pytest --cov=src tests/
# Lint and fix style and lint type-hinting
lint:
	@poetry run ruff format src tests
	@poetry run ruff check --fix src tests
	@poetry run mypy src tests
# Lint style and lint type-hinting
lint-ci:
	@poetry run ruff format --check src tests
	@poetry run ruff check src tests
	@poetry run mypy src tests