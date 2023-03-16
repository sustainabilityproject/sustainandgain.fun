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

## Run

```bash
python manage.py runserver 8000
```

## Test
```bash
python manage.py test
```

## Structure
The project is set up as a typical Django project. Different Django apps handle different parts of the app's
functionality. 
```
├───accounts
│   └───migrations
├───autoencoder
│   └───src
├───chat
│   └───migrations
├───feed
│   └───migrations
├───friends
│   ├───migrations
│   ├───templatetags
│   └───tests
├───leagues
│   ├───migrations
│   └───tests
├───media
│   ├───bin
│   ├───default
│   └───task_photos
├───promotional things
│   ├───Images
│   └───logo design
├───static
├───sustainability
│   ├───tests
│   │   └───factories
│   └───__pycache__
├───tasks
│   ├───migrations
│   ├───templatetags
│   └───tests
├───templates
│   ├───account
│   ├───admin
│   ├───chat
│   ├───feed
│   ├───friends
│   ├───leagues
│   ├───notifications
│   └───tasks
└───worker
    └───src
   ```
Functionality is divided across apps which have their own views, URLs and models.
* *sustainability* is the base app, containing the settings and delegating URLs to the correct apps.
* *accounts* manages user creation and authentication, based on the inbuilt Django user system.
* *autoencoder* contains the from-scratch machine learning system we have implemented for automatic task validation
* *chat* contains the global site chat system
* *feed* contains the feed of completed tasks that users see by default when they are logged in
* *friends* manages friend requests and the profile system
* *leagues* contains the league system which allows users to join leagues and compete with each other
* *tasks* contains models and views for the tasks which users accept and complete

There are also some folders which are not Django apps:
* *media* contains the uploaded task photos
* *promotional things* contains client-focused branding material and imagery
* *static* contains static, unchanging resources which need to be loaded elsewhere such as the favicon
* *templates* contains the Django HTML templates which are displayed to users via views

## Additional resources
We have a [Kanban board](https://trello.com/b/DwykNGu4/kanban-board) on Trello, and a [documentation website](https://docs.sustainandgain.fun/) which contains client-focused explanations of the app.

