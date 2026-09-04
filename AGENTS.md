# AGENTS instructions

Important context for AI coding agents working on this project.

## Development commands

> **Note:** Run commands via `just`, which invokes `uv` to manage the virtual environment automatically.

-   `just lint`: Lint the project.
-   `just format`: Format project files.
-   `just test`: Run tests.
-   `just translations`: Generate and compile translation strings.

## Setup & run commands

-   `just backend`:Build the backend.
-   `just frontend`:Build the frontend.
-   `just buildfixtures`:Build the test fixtures.
-   `just run`: Run the development server.

## Docker setup

Create a `.env` file in the project root with:

```
ALLOWED_HOSTS=localhost
PORT=8000
SECRET_KEY=some-random-secret
DJANGO_SETTINGS_MODULE=apps.guide.settings.dev
```

### Docker commands

-   `docker compose up --remove-orphans`: Build (if needed) and run the container.
-   `docker compose exec web bash`: Open a shell in the container. The container bundles Python
    and Node, so the same `just` commands (e.g. `just backend`, `just frontend`) work from there.
-   `docker compose build`: Rebuild the image after a dependency change.

## Coding style & naming conventions

Defined in `ruff.toml`, `.eslintrc.json`, `.prettierrc.json`, `.stylelintrc.json`:

-   **Python**: 4 spaces indent, `ruff format` (line-length 88, target py312)
-   **JavaScript**: `eslint` with `@wagtail/eslint-config-wagtail`
-   **Formatting**: `prettier` (`singleQuote`, `trailingComma: all`)
-   **SCSS/CSS**: `stylelint` with `@wagtail/stylelint-config-wagtail` (strict color values)
-   **Tests**: modules named `test_*.py`, classes named `Test*`, methods named `test_*`

## Commit & pull request guidelines

-   Be concise and to the point. Explain rationales that aren’t obvious.
-   Commit messages must be a single line, short, sentence case, imperative summary. Do not add a description body unless explicitly asked.
-   Always add a disclaimer to the PR description mentioning how AI agents are involved with the contribution.
-   Do not add commits unrelated to the PR — check commit history against upstream main before pushing.
