#!/bin/bash

# Wait for Postgres to start
# Replace "db:5432" with your database service name and port
# while ! nc -z db 5432; do
#   sleep 1
# done

# Django setup
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata categories.json
python manage.py loaddata categories_mso.json
python manage.py loaddata currency.json

# Run the application
exec "$@"