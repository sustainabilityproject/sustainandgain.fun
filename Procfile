web: gunicorn sustainability.wsgi:application

worker: ./worker/target/release/worker

release: django-admin migrate --no-input && django-admin collectstatic --no-input && cd worker && cargo build --release