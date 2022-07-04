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

### Frontend

- Setup the appropriate version of node.

      nvm use

    Check the Node version number. It should be `V16.*`

      node -v

- Install all the dependencies

      yarn

- Develop the frontend, run a file watcher

      yarn start

    Or, create a production build

      yarn build

### Backend

- Verify that your python version is `3.9.*`

      python -V

- Setup virtual environment

    ``` bash
    python -m venv env
    source env/bin/activate
    ```

- Install the required dependencies

      python -m pip install requirements.txt

- Apply migrations

      python manage.py migrate

- Create a super-user

      python manage.py createsuperuser
      
- Start the server

      python manage.py runserver
