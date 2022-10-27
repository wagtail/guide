ifneq (,$(wildcard ./.env))
    include .env
    export
endif

buildfixtures:
	poetry run python manage.py buildfixtures

test:
	DJANGO_SETTINGS_MODULE=apps.guide.settings.test poetry run python manage.py test

test-coverage:
	poetry run coverage run manage.py test && poetry run coverage report

format-backend:
	poetry run isort apps
	poetry run black apps

format-frontend:
	npm run format

format: format-backend format-frontend

lint-backend:
	poetry run flake8 apps
	poetry run isort --check-only --diff apps
	poetry run black --check --diff apps

lint-frontend:
	npm run lint

lint: lint-backend lint-frontend

frontend:
	npm ci
	npm run build

backend:
	poetry install
	poetry run python manage.py migrate
	poetry run python manage.py createcachetable
	poetry run python manage.py createsuperuser

run:
	poetry run python manage.py runserver

docker-build:
	docker-compose build

docker-run:
	docker-compose up

docker-shell:
	docker-compose exec web bash

docker-shell-frontend:
	docker-compose exec frontend bash

docker-init:
	docker-compose exec web poetry install
	docker-compose exec web poetry run python manage.py migrate
	docker-compose exec web poetry run python manage.py createcachetable
	docker-compose exec web poetry run python manage.py createsuperuser
	docker-compose exec web poetry run python manage.py buildfixtures

