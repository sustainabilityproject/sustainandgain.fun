web: gunicorn sustainability.wsgi:application

worker: cd worker && cargo run

release: django-admin migrate --no-input && django-admin collectstatic --no-input