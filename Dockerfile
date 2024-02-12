FROM python:3.10.6

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV POETRY_VIRTUALENVS_CREATE=false
ENV PATH="/root/.local/bin:$PATH"

WORKDIR /code
COPY poetry.lock pyproject.toml /code/

RUN poetry install  --no-interaction --no-ansi --only main

COPY ./src /code/src

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]