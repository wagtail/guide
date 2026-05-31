# AGENTS instructions

Important context for AI coding agents working on this project.

## Development commands

> **Note:** Run `source "$(poetry env activate)"` before any `make` command, These require the Poetry virtual environment to be active.

-   `make lint`: Lint the project.
-   `make format`: Format project files.
-   `make test`: Run tests.
-   `make translations`: Generate and compile translation strings.

## Setup & run commands

-   `make backend`:Build the backend.
-   `make frontend`:Build the frontend.
-   `make buildfixtures`:Build the test fixtures.
-   `make run`: Run the development server.

## Docker setup

Create a `.env` file in the project root with:

```
ALLOWED_HOSTS=localhost
PORT=8000
SECRET_KEY=some-random-secret
DJANGO_SETTINGS_MODULE=apps.guide.settings.dev
```

### Docker commands

-   `make docker-build`: Build the Docker image.
-   `make docker-run`: Run the Docker container.
-   `make docker-init`: Initialize the project inside the container.

## Coding style & naming conventions

Defined in `ruff.toml`, `.eslintrc.json`, `.prettierrc.json`, `.stylelintrc.json`:

-   **Python**: 4 spaces indent, `ruff format` (line-length 88, target py312)
-   **JavaScript**: `eslint` with `@wagtail/eslint-config-wagtail`
-   **Formatting**: `prettier` (`singleQuote`, `trailingComma: all`)
-   **SCSS/CSS**: `stylelint` with `@wagtail/stylelint-config-wagtail` (strict color values)
-   **Tests**: modules named `test_*.py`, classes named `Test*`, methods named `test_*`

## Commit & pull request guidelines

-   Be concise and to the point. Explain rationales that aren’t obvious.
-   Recent commit messages use short, capitalized, imperative summaries (e.g., “Enforce additional mypy check”).
-   Always add a disclaimer to the PR description mentioning how AI agents are involved with the contribution.
-   Do not add commits unrelated to the PR — check commit history against upstream main before pushing.
