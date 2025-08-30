release: python manage.py migrate
web: gunicorn auth_service.wsgi:application --log-file -