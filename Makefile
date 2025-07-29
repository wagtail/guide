ifneq (,$(wildcard ./.env))
    include .env
    export
endif

buildfixtures:
	poetry run python manage.py buildfixtures

test: lint
	DJANGO_SETTINGS_MODULE=apps.guide.settings.test poetry run python manage.py test

test-coverage:
	poetry run coverage run manage.py test && poetry run coverage report

format-backend:
	poetry run ruff check . --fix
	poetry run black .

format-frontend:
	npm run format

format: format-backend format-frontend

lint-backend:
	poetry run ruff check .
	poetry run black --check --diff .

lint-frontend:
	npm run lint

lint: lint-backend lint-frontend

frontend:
	npm ci
	npm run build

backend: compilemessages
	poetry install --no-root
	poetry run python manage.py migrate
	poetry run python manage.py createcachetable
	poetry run python manage.py createsuperuser

run:
	poetry run python manage.py runserver


translations: makemessages compilemessages

makemessages:
	cd apps && poetry run python ../manage.py makemessages --all --no-location
	cd apps && poetry run python ../manage.py makemessages --all --no-location -e ".js" -d djangojs --ignore=frontend/static/*

compilemessages:
	cd apps && poetry run python ../manage.py compilemessages

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

