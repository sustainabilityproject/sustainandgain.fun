# Sustainability Project

## Setup

Install pipenv

```bash
pip install pipenv
```

Set values in `.env`

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

## Enable AI (optional)

Run the following command to enable the AI

```bash
python manage.py enableai
```

## Run

```bash
python manage.py runserver 8000
```

## Test
```bash
python manage.py test
```
