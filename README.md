# Guide

A website to teach Wagtail CMS to content editors, moderators and administrators.

Wagtail guide brings you:
- Tutorials, 
- How-to, 
- Reference 
- Background information


## Google Summer of Code

This project is a part of Google Summer of Code 2022 under the organization [**Wagtail**](https://wagtail.org/). Find more details about the project [here](https://summerofcode.withgoogle.com/programs/2022/projects/7nMw2hTq).


## Development

We assume that you have basic knowledge of Node/Yarn/Webpack and Python/Django/Wagtail.

### Frontend

Use `Node V16.*`. Run `make frontend`.

Often used commands for more control:  

    nvm use
    node -v
    # V16.*
    yarn
    yarn start
    yarn build


### Backend

Use `Python 3.9.*` (virtual environment). Run `make backend` and `make run`.

Often used commands for more control:

    python -V
    # Python 3.9.*
    python -m venv env
    source env/bin/activate
    python -m pip install requirements.txt
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py buildfixtures
    python manage.py runserver


# Gitpod

Launch a ready-to-code Wagtail Guide development environment with a single click.

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/wagtail/guide)

Steps:

1. Click the ``Open in Gitpod`` button.
2. Relax: a development environment with an active Wagtail Guide site will be created for you.
3. Login at `/admin/` with username `admin` and password `changeme`
