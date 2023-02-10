# Sustainability Project

## Setup

Install pipenv

```bash
pip install pipenv
```

Enter virtual environment

```bash
pipenv shell
```

Install dependencies

```bash
pipenv sync
```

Migrate database

```bash
python manage.py migrate
```

Create an admin user

```bash
python manage.py createsuperuser
```

## Run

```bash
python manage.py runserver 8000
```