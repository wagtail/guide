buildfixtures:
	python manage.py buildfixtures

test:
	python manage.py test

test-coverage:
	coverage run manage.py test && coverage report

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
	python -m pip install -r requirements.txt
	python manage.py migrate
	python manage.py createsuperuser

run:
	python manage.py runserver