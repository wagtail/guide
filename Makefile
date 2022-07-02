format:
	black --target-version py37 .
	isort .

lint:
	black --target-version py37 --check --diff .
	isort --check-only --diff