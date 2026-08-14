# Task runner: https://github.com/casey/just
# Requires: `uv`, `npm`, and `just`.

# Load environment variables from a `.env` file, if present.
set dotenv-load

# List all the justfile recipes.
help:
    just --list --list-prefix 'just '

# Build the test fixtures.
buildfixtures:
    uv run python manage.py buildfixtures

# Run tests with the test settings.
test:
    DJANGO_SETTINGS_MODULE=apps.guide.settings.test uv run python manage.py test

# Run tests with coverage.
test-coverage:
    uv run coverage run manage.py test
    uv run coverage report

# Format the backend code with Ruff.
format-backend:
    uv run ruff check . --fix
    uv run ruff format .

# Format the frontend code with Prettier.
format-frontend:
    npm run format

# Run all formatters.
format: format-backend format-frontend

# Lint the backend code with Ruff.
lint-backend:
    uv run ruff check .
    uv run ruff format --check .

# Lint the frontend code.
lint-frontend:
    npm run lint

# Run all linters.
lint: lint-backend lint-frontend

# Install frontend dependencies and build the static files.
frontend:
    npm ci
    npm run build

# Install backend dependencies and initialise the database.
backend:
    uv sync
    uv run python manage.py migrate
    uv run python manage.py createcachetable
    uv run python manage.py createsuperuser

# Run the development server.
run:
    uv run python manage.py runserver

# Generate and compile translation strings.
translations: makemessages compilemessages

# Generate translation strings.
makemessages:
    cd apps && uv run python ../manage.py makemessages --all --no-location
    cd apps && uv run python ../manage.py makemessages --all --no-location -e ".js" -d djangojs --ignore=frontend/static/*

# Compile translation strings.
compilemessages:
    cd apps && uv run python ../manage.py compilemessages

# Build the Docker image.
docker-build:
    docker compose build

# Run the Docker container in the foreground.
docker-run:
    docker compose up --remove-orphans

# Run the Docker container in the background.
docker-start:
    docker compose up --remove-orphans -d

# Stop the Docker container.
docker-stop:
    docker compose down

# Open a shell in the running Docker container.
docker-exec:
    docker compose exec web /bin/bash

# Initialise the project inside the Docker container.
docker-init:
    docker compose exec web uv run python manage.py migrate
    docker compose exec web uv run python manage.py createcachetable
    docker compose exec web uv run python manage.py createsuperuser
