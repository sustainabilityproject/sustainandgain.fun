![Sustain+Gain](./static/logo/sustain-gain.svg)
Sustain and Gain is a mobile web app where users compete to earn points by completing sustainable tasks.

## Contents
1. [Setting up and running the app](#setting-up-and-running-the-app)
2. [Project Structure](#project-structure)
3. [Documentation](#documentation)
4. [Contact](#contact)
# Setting up and running the app


## Setup

### Requirements

- Python 3.7+
- [Docker](https://docs.docker.com/get-docker/)
- [Rust](https://rustup.rs/) (optional)

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

Initialise Sustainability Steve

```bash
python manage.py create_sustainability_steve
```

## Enable AI (optional)

Install [PyTorch](https://pytorch.org/get-started/locally/) and [Transformers](https://pypi.org/project/transformers/) with pip.

Change the value of AI in `.env` to `1`.

## Run

### Services

Run local email server and Redis with the following

```bash
docker compose up
```

You can now view emails by going to [http://localhost:8025](http://localhost:8025)

> If you do not want to verify emails, you can set `ACCOUNT_EMAIL_VERIFICATION = 'none'` in `sustainability/settings.py`

### Server

```bash
python manage.py runserver 8000
```

### Background workers (optional)

#### Auto assign tasks to users

```bash
celery -A sustainability worker -l INFO -B
```

#### Email Notifications

Sending emails uses a Rust worker. To run this, first install [Rust](https://rustup.rs/).
You will also need to configure the app to use Postgres which is already setup by Docker.
Set the following values in `.env`:

```bash
DATABASE_URL=postgres://sustain:sustain@localhost:5432/sustain
```

You will need to remigrate the database to use Postgres:

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py create_sustainability_steve
```

Then run the worker:

```bash
cd worker && cargo run --release
```

## Test
The test suite can be run using the default Django test command:
```bash
python manage.py test
```
This discovers and runs all tests in files with names like ```*test.py```
.
Additionally, the test suite is automatically run via GitHub actions for pushes, merges and pull requests.

Each Django app has a ```tests``` folder containing the tests for that app - read more about project structure
[below](#project-structure).

# Project Structure
The project is set up as a typical Django project. Most directories are Django apps, which handle different parts of the application's
functionality.

### A typical Django app
Most of our project's directories are Django apps. A typical Django app is set up like this:
```
│   admin.py            Defines which models in this app are editable from the admin page.         
│   forms.py            Define forms which are relevant to this app's models.
│   models.py           Models contain essential fields and behaviors of the data stored, typically mapped to a database
│   signals.py          Signals notify another Django app when some behaviour takes place.
│   urls.py             Map website URLs to Django views.
│   views.py            Define the web responses to give a user based on a web request.
│
├───migrations          Generated information used to build the models database.
│
└───tests               Tests for each Django app are within that app.
        factories.py    Allow the building of 'default' models to make writing tests easier.
        test_models.py  A test file automatically run when the test suite is run.
```
### Project file structure
Below is the overall product structure. Most directories are Django apps (see above) - where directories are not Django
apps, an explanation has been provided.
```
├───.github         Contains GitHub-specific information
│   └───workflows   Actions automatically run on GitHub pushes (running tests, deployment)
│
├───about        A Django app that manages the 'about' page containing contact information and policies (see above for Django app structure)
│   
├───accounts        A Django app that manages accounts and authentication (see above for Django app structure)
│
├───feed            A Django app that manages the home feed users see (see above for Django app structure)
│   
├───friends         A Django app that manages the friend system (see above for Django app structure)
│   
├───imagenet        An imported AI solution for automatically validating tasks.
│   
├───leagues         A Django app that manages leagues users compete in (see above for Django app structure)
│   
├───media           Stores media such as user profile pictures and uploaded images.
│  
├───static              Contains static resources which need to be loaded elsewhere like the favicon.
│
├───sustainability      The base Django app, containing settings and configuration.
│  
├───tasks               A Django app that manages tasks (see above for Django app structure)
│  
├───templates           Contains the Django HTML templates displayed to users via views 
│   
└───worker              Contains the Rust background worker which handles automatic emailing, bomb task countdowns etc.
   ```
## Documentation
Code is commented with Python docstrings.

We have a user-focused [documentation website](https://docs.sustainandgain.fun/) which explains the app's features, as
well as promotional documents in the 'promotional things' folder including a site overview, logo designs and images.

Additionally, we have a [Kanban board](https://trello.com/b/DwykNGu4/kanban-board) on Trello to manage the agile process.

# Contact
For general concerns, please email contact@sustainandgain.fun

## Developer Contact
If you need to contact the developers directly, our emails are listed below.
- cms@sustainandgain.fun
- charlie@sustainandgain.fun
- nicholas@sustainandgain.fun
- james@sustainandgain.fun
- annabelle@sustainandgain.fun
- harry@sustainandgain.fun
