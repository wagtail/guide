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

# Run all tests.
test: test-backend test-frontend

# Run the backend tests with the test settings.
test-backend:
    DJANGO_SETTINGS_MODULE=apps.guide.settings.test uv run python manage.py test

# Run the frontend tests with Vitest.
test-frontend:
    npm test

# Run the backend tests with coverage.
test-coverage:
    DJANGO_SETTINGS_MODULE=apps.guide.settings.test uv run coverage run manage.py test
    uv run coverage report

# Format the backend code with Ruff.
format-backend:
    uv run ruff check . --fix
    uv run ruff format .

# Format the frontend code with Oxfmt.
format-frontend:
    npm run format

# Run all formatters.
format: format-backend format-frontend

# Lint the backend code with Ruff.
lint-backend:
    uv run ruff check .
    uv run ruff format --check .

# Lint the frontend code with Oxlint, Oxfmt, and Stylelint.
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
    ./content/evals/translations-inspect_ai/translation_task.py "$@"

# Export Wagtail admin UI translations as eval glossaries, per language code.
eval-glossary *LANGS="ar":
    uv run python content/evals/translations-inspect_ai/export_glossary.py {{ LANGS }}

# Run the Promptfoo translation eval across all candidate models (Scaleway).
eval-promptfoo *ARGS:
    npx --yes promptfoo@latest eval -c content/evals/translations/translations.yaml "$@"

# Browse Promptfoo translation eval results.
eval-promptfoo-view:
    npx --yes promptfoo@latest view --yes

# Where the agent readiness eval keeps its empty working directory and proxy log:
# outside the repository, so that no arm can read the guide's content copy.
eval_agents_cache := env("XDG_CACHE_HOME", env("HOME") / ".cache") / "guide-agent-eval"

# Install the agent readiness eval tooling, without saving it to package.json.
# promptfoo only resolves the Claude Agent SDK from the project's node_modules,
# and a later `npm ci` prunes both.
eval-agents-init:
    npm install --no-save promptfoo@0.124.1 @anthropic-ai/claude-agent-sdk@0.3.296

# Run the proxy that logs agents' guide requests, forwarding them to the local
# development server (`local`) or to the live site (`prod`). Port 8899 serves
# the site as it is, port 8898 a plain site without agent readiness features.
eval-agents-proxy target="local":
    mkdir -p "{{ eval_agents_cache }}"
    EVAL_PROXY_LOG="{{ eval_agents_cache }}/requests.jsonl" \
    uvx --from mitmproxy==12.2.3 mitmdump --mode regular@8899 --mode regular@8898 \
        --allow-hosts '^guide\.wagtail\.org(:443)?$' \
        {{ if target == "local" { "--map-remote '|https://guide\\.wagtail\\.org/|http://localhost:8000/'" } else { "" } }} \
        -s content/evals/agent-readiness/proxy.py

# Check the agent readiness eval's cases against their checks, without calling a model.
eval-agents-check:
    uv run python content/evals/agent-readiness/graders/check_cases.py

# Run the agent readiness eval on a Claude model (like `just eval-agents claude-haiku-5-5 --repeat 3`).
eval-agents model="claude-sonnet-5-5" *ARGS: eval-agents-check
    @test -d node_modules/@anthropic-ai/claude-agent-sdk || { echo 'Claude Agent SDK not found - run `just eval-agents-init`'; exit 1; }
    @curl -s -o /dev/null http://127.0.0.1:8899 || { echo 'Proxy not running - start `just eval-agents-proxy` in another terminal'; exit 1; }
    mkdir -p "{{ eval_agents_cache }}/empty"
    # The CA bundle curl uses in the web+curl arm: system certificates and the proxy's.
    cat /etc/ssl/cert.pem "$HOME/.mitmproxy/mitmproxy-ca-cert.pem" > "{{ eval_agents_cache }}/ca-bundle.pem"
    # `shift` drops the model, so "$@" passes the other arguments through quoted.
    shift; \
    HTTPS_PROXY=http://127.0.0.1:8899 \
    NODE_EXTRA_CA_CERTS="$HOME/.mitmproxy/mitmproxy-ca-cert.pem" \
    EVAL_AGENTS_MODEL="{{ model }}" \
    EVAL_AGENTS_FIXTURES="{{ eval_agents_cache }}" \
    PROMPTFOO_PYTHON="$PWD/.venv/bin/python" \
    npx promptfoo eval -c content/evals/agent-readiness/agent-readiness.yaml --no-cache "$@"

# Browse agent readiness eval results.
eval-agents-view:
    npx promptfoo view --yes

# Browse translation eval results in the Inspect viewer.
eval-view:
    uvx --from inspect-ai --python 3.12 inspect view --log-dir content/evals/translations-inspect_ai/logs
