run:
	python manage.py runserver

test:
	flake8 apps
	isort --check-only --diff apps
	black --check --diff apps
	python manage.py test

format:
	isort apps
	black apps

lint:
	flake8 apps
	isort --check-only --diff apps
	black --check --diff apps
