web: gunicorn sustainability.wsgi:application

worker: ./worker/worker

release: django-admin migrate --no-input && django-admin collectstatic --no-input