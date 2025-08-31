#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
until pg_isready -h db -p 5432 -U postgres; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Wait for Redis to be ready
until redis-cli -h redis ping; do
  echo "Waiting for Redis to be ready..."
  sleep 2
done

# Run database migrations
echo "Running database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create test data if in development
if [ "$DEBUG" = "True" ]; then
  echo "Creating test data..."
  python manage.py create_test_data
fi

# Start the Django application
echo "Starting Django application..."
exec gunicorn auth_service.wsgi:application --bind 0.0.0.0:8000 --workers 3