FROM python:3.10.6-alpine AS builder
WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN apk add --no-cache build-base libffi-dev curl netcat-openbsd
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_HOME=/usr/local \
    POETRY_VERSION=1.7.1
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    poetry install  --no-interaction --no-ansi --only main

# - - - - - - - - - - - - - - - - - - - - #

FROM python:3.10.6-alpine
WORKDIR /code

COPY --from=builder /code /code
COPY --from=builder /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/
COPY ./src /code/src
COPY ./alembic.ini /code/alembic.ini
COPY ./alembic /code/alembic
COPY entrypoint.sh /code/entrypoint.sh

RUN chmod +x /code/entrypoint.sh && \
    addgroup --gid 1000 pyweb && \
    adduser pyweb -h /code -u 1000 -G pyweb -DH
USER 1000

ENTRYPOINT ["/code/entrypoint.sh"]
