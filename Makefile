install:
	poetry install
build:
	docker build -t pyweb-image .
run:
	docker-compose up -d
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
run-docker:
	docker run -d --name epam-pyweb -p 80:80 pyweb-image
stop-docker:
	docker stop epam-pyweb
	docker rm epam-pyweb
clean-docker:
	docker stop epam-pyweb
	docker rm epam-pyweb
	docker rmi pyweb-image