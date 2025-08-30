#!/bin/bash

echo "Starting deployment process..."

# Check if required environment variables are set
if [ -z "$DATABASE_URL" ] || [ -z "$REDIS_URL" ] || [ -z "$SECRET_KEY" ]; then
    echo "Error: Required environment variables are not set"
    echo "Please ensure DATABASE_URL, REDIS_URL, and SECRET_KEY are configured"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements/prod.txt

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Run tests
echo "Running tests..."
python manage.py test --keepdb

echo "Deployment completed successfully!"