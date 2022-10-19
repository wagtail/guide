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
