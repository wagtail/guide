# Task runner: https://github.com/casey/just
# Requires: `uv`, `npm`, and `just`.

# Load environment variables from a `.env` file, if present.
set dotenv-load
# Pass recipe arguments through as "$@" so quoted arguments survive.
set positional-arguments

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
    DJANGO_SETTINGS_MODULE=apps.guide.settings.test uv run coverage run manage.py test
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

# Evaluate translation quality of candidate LLMs with Inspect AI (Scaleway).
eval-translations *ARGS:
    ./prompts/evals/translations-inspect_ai/translation_task.py "$@"

# Export Wagtail admin UI translations as eval glossaries, per language code.
eval-glossary *LANGS="ar":
    uv run python prompts/evals/translations-inspect_ai/export_glossary.py {{ LANGS }}

# Run the Promptfoo translation eval across all candidate models (Scaleway).
eval-promptfoo *ARGS:
    npx --yes promptfoo@latest eval -c prompts/evals/translations/translations.yaml "$@"

# Browse Promptfoo translation eval results.
eval-promptfoo-view:
    npx --yes promptfoo@latest view --yes

# Browse translation eval results in the Inspect viewer.
eval-view:
    uvx --from inspect-ai --python 3.12 inspect view --log-dir prompts/evals/translations-inspect_ai/logs
