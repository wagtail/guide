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
	poetry install --no-root
	poetry run python manage.py migrate
	poetry run python manage.py createcachetable
	poetry run python manage.py createsuperuser
	poetry run python manage.py compilemessages

run:
	poetry run python manage.py runserver


translations: makemessages compilemessages

makemessages:
	cd apps && poetry run python ../manage.py makemessages --all --no-location
	cd apps && poetry run python ../manage.py makemessages --all --no-location -e ".js" -d djangojs --ignore=frontend/static/*

compilemessages:
	cd apps && poetry run python ../manage.py compilemessages

docker-build:
	docker build -t guide:latest --build-arg POETRY_INSTALL_ARGS="" -f Dockerfile .

docker-run:
	docker run --name guide_latest -p ${PORT}:${PORT} --env-file .env guide:latest sh -c 'poetry run python manage.py runserver 0.0.0.0:${PORT}'

docker-exec:
	docker exec -it guide_latest /bin/bash

docker-init:
	docker exec -it guide_latest /bin/bash -c "make backend"
