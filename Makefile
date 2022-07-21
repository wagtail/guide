buildfixtures:
	python manage.py buildfixtures

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

frontend:
	yarn
	yarn build

backend:
	python pip install -r requirements.txt
	python manage.py migrate
	python manage.py createsuperuser

run:
	python manage.py runserver
