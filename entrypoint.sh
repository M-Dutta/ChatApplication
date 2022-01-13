#!/usr/bin/env bash

echo "Waiting for postgres..."

while ! nc -z db 5432; do
  sleep 0.1
done

echo "PostgreSQL started"

echo "Making Migration Plans"
python manage.py makemigrations chatApplication

echo "Running Migrations"
python manage.py migrate chatApplication

echo "Run Server"
python ./manage.py runserver 0.0.0.0:8001
exec "$@"