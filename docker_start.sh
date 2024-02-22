#!/bin/sh

# Run migrations
/code/.venv/bin/alembic upgrade head

# Start the application
if [ "$RELOAD" = "true" ]
then
  /code/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 80 --reload
else
  /code/.venv/bin/uvicorn src.main:app --host 0.0.0.0 --port 80
fi
