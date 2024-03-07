#!/bin/sh

echo "Waiting for PostgreSQL..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done
echo "PostgreSQL started"

echo "Running migrations..."
alembic upgrade head
echo "Migrations done"

if [ "$RELOAD" = "true" ]
then
uvicorn src.main:app --host 0.0.0.0 --reload
else
uvicorn src.main:app --host 0.0.0.0
fi

exec "$@"