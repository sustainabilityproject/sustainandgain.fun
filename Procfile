web: gunicorn sustainability.wsgi:application

worker: python manage.py process_tasks

release: django-admin migrate --no-input && django-admin collectstatic --no-input