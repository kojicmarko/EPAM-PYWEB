install:
	poetry install
run:
	uvicorn src.main:app
lint:
	ruff format
	ruff check --fix
	mypy src tests
build-docker:
	docker build -t pyweb-image .
run-docker:
	docker run -d --name epam-pyweb -p 80:80 pyweb-image
run-docker-reload:
	docker-compose up -d
stop-docker:
	docker stop epam-pyweb
	docker rm epam-pyweb
stop-docker-reload:
	docker-compose down --volumes
clean-docker:
	docker stop epam-pyweb
	docker rm epam-pyweb
	docker rmi pyweb-image