web: python manage.py collectstatic --noinput && gunicorn tacklog.wsgi --bind 0.0.0.0:$PORT
release: python manage.py migrate