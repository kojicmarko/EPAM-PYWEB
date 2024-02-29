# TODO: Commands could be cleaned up

install:
	poetry install
build:
	docker-compose build -t pyweb-image .
run:
	poetry run uvicorn src.main:app --port 80
stop:
	docker-compose down --volumes
lint:
	poetry run ruff format src tests
	poetry run ruff check --fix src tests
	poetry run mypy src tests
lint-ci:
	poetry run ruff format --check src tests
	poetry run ruff check src tests
	poetry run mypy src tests
test:
	poetry run pytest --cov=src tests/
docker-run:
	docker-compose up -d --build
docker-stop:
	docker-compose down --volumes