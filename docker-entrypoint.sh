#!/bin/bash

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate
echo "collectstatic"
python manage.py collectstatic --noinput
exec "$@"