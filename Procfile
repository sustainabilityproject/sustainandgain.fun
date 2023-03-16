web: gunicorn sustainability.wsgi:application

release: python3 -m pip install torch transformers && django-admin migrate --no-input && django-admin collectstatic --no-input