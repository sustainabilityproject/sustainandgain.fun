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

Install [PyTorch](https://pytorch.org/get-started/locally/) and [Transformers](https://pypi.org/project/transformers/) with pip.

Change the value of AI in `.env` to `1`.

## Run

### Local email

You will need [docker](https://docs.docker.com/get-docker/) installed.

Run local email server with the following

```bash
docker compose up
```

You can now view emails by going to [http://localhost:8025](http://localhost:8025)

### Server

```bash
python manage.py runserver 8000
```

## Test
```bash
python manage.py test
```
