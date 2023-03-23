web: gunicorn sustainability.wsgi:application

worker: celery -A sustainability worker -l INFO -B

release: django-admin migrate --no-input && django-admin collectstatic --no-input