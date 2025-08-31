#!/bin/bash

echo "Setting up local development environment..."

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "PostgreSQL is not running. Please start PostgreSQL service."
    echo "On macOS: brew services start postgresql"
    echo "On Ubuntu: sudo service postgresql start"
fi

# Check if Redis is running
if ! redis-cli ping > /dev/null 2>&1; then
    echo "Redis is not running. Please start Redis service."
    echo "On macOS: brew services start redis"
    echo "On Ubuntu: sudo service redis-server start"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "auth_env" ]; then
    echo "Creating virtual environment..."
    python -m venv auth_env
fi

# Activate virtual environment
echo "Activating virtual environment..."
source auth_env/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements/dev.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env file with your database and Redis credentials"
fi

# Run migrations
echo "Running database migrations..."
python manage.py migrate

# Create superuser
echo "Creating superuser account..."
python manage.py createsuperuser --noinput --email admin@example.com || true

# Create test data
echo "Creating test data..."
python manage.py create_test_data

echo "Local setup completed successfully!"
echo "Start the development server with: python manage.py runserver"