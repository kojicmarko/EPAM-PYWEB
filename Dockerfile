FROM python:3.10.6-alpine AS builder
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN apk add build-base libffi-dev curl
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_HOME=/usr/local \
    POETRY_VERSION=1.7.1
RUN curl -sSL https://install.python-poetry.org | python3 -

RUN poetry install  --no-interaction --no-ansi --only main

# - - - - - - - - - - - - - - - - - - - - #

FROM python:3.10.6-alpine
WORKDIR /code

COPY --from=builder /code /code
COPY ./src /code/src

RUN addgroup --gid 1000 pyweb
RUN adduser pyweb -h /code -u 1000 -G pyweb -DH
USER 1000

CMD ["/code/.venv/bin/uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
