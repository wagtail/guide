include .env

buildfixtures:
	poetry run python manage.py buildfixtures

test:
	DJANGO_SETTINGS_MODULE=apps.guide.settings.test poetry run python manage.py test

test-coverage:
	poetry run coverage run manage.py test && poetry run coverage report

format:
	poetry run isort apps
	poetry run black apps
	yarn format

lint:
	poetry run flake8 apps
	poetry run isort --check-only --diff apps
	poetry run black --check --diff apps
	yarn lint

frontend:
	yarn
	yarn build

backend:
	poetry install
	poetry run python manage.py migrate
	poetry run python manage.py createcachetable
	poetry run python manage.py createsuperuser

run:
	poetry run python manage.py runserver

docker-build:
	docker build -t guide:latest --build-arg POETRY_INSTALL_ARGS="" -f Dockerfile .

docker-run:
	docker run --name guide_latest -p 8200:8200 --env-file .env guide:latest sh -c 'poetry run python manage.py runserver 0.0.0.0:${PORT}'

docker-exec:
	docker exec -it guide_latest /bin/bash

docker-init:
	docker exec -it guide_latest /bin/bash -c "make backend"