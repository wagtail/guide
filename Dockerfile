# syntax=docker/dockerfile:1.10
# check=error=true

# Opt into newer Dockerfile syntax, make `docker build .` fail on warnings
# See https://docs.docker.com/reference/build-checks/.
# Run `docker build --check .` for better error messages.

# frontend stages

# Keep the Node version in sync with the dev stage below and .nvmrc.
FROM node:26 AS frontend-deps

# Make build & post-install scripts behave as if in CI (e.g. logging verbosity).
ARG CI=true

# Split from frontend-build so the dev stage below can reuse node_modules
# without needing to run the production build.
COPY package.json package-lock.json webpack.config.js ./
RUN --mount=type=cache,target=/root/.npm npm ci

FROM frontend-deps AS frontend-build

COPY ./apps/frontend/static_src/ ./apps/frontend/static_src/
RUN npm run build

# base stage

# Debian over alpine: it's considered more stable (different C compiler) and
# ships with the packages commonly needed for image manipulation, at the
# cost of a larger (~1.5GiB) image.
FROM python:3.14 AS base

# Keep this version in sync with the local `uv` used to generate uv.lock.
COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /uvx /bin/

ENV VIRTUAL_ENV=/venv

RUN useradd guide --create-home && mkdir /app $VIRTUAL_ENV && chown -R guide /app $VIRTUAL_ENV

WORKDIR /app

# Defaults only: any environment variables set on Heroku override these.
#  * UV_PROJECT_ENVIRONMENT - installs into $VIRTUAL_ENV instead of the
#    project's default `.venv`, so it isn't clobbered by a bind mount in dev.
#  * UV_LINK_MODE=copy - hardlinks break across Docker layers.
#  * PYTHONUNBUFFERED - otherwise logs can be lost if the process crashes:
#    https://docs.python.org/3.14/using/cmdline.html#envvar-PYTHONUNBUFFERED
#  * PORT - read by Gunicorn; Heroku sets this itself and ignores EXPOSE.
ENV PATH=$VIRTUAL_ENV/bin:$PATH \
    UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PORT=8000

EXPOSE 8000

# Heroku doesn't run containers as root either:
# https://devcenter.heroku.com/articles/container-registry-and-runtime#dockerfile-commands-and-runtime
USER guide

RUN python -m venv $VIRTUAL_ENV
COPY --chown=guide pyproject.toml uv.lock ./


# dev stage

# Used by `docker compose` for local development. Application code isn't
# copied in at build time - docker-compose bind mounts it instead - so only
# rebuild this image when dependencies change (`docker compose build`).
FROM base AS dev

USER root

# Node's major version is kept in sync with frontend-deps above and .nvmrc.
# `just` is installed too, so the recipes in ./justfile also work from a
# shell in this container, the same way they do on the host.
RUN --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    --mount=type=cache,target=/var/cache/apt,sharing=locked \
    mkdir -p /etc/apt/keyrings \
    && apt-get --quiet --yes update \
    && apt-get --quiet --yes install --no-install-recommends ca-certificates curl gnupg \
    && curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_26.x nodistro main" > /etc/apt/sources.list.d/nodesource.list \
    && apt-get --quiet --yes update \
    && apt-get --quiet --yes install --no-install-recommends nodejs just

USER guide

ARG UV_SYNC_ARGS="--all-groups"
RUN uv sync --frozen ${UV_SYNC_ARGS}

# Reuses node_modules from frontend-deps so a freshly built container doesn't
# need to `npm ci` before assets can be built. docker-compose.yml volumes
# node_modules so it isn't shadowed by the code bind mount.
COPY --chown=guide --from=frontend-deps ./node_modules ./node_modules
COPY --chown=guide package.json package-lock.json webpack.config.js ./

CMD ["uv", "run", "python", "manage.py", "runserver", "0.0.0.0:8000"]


# production stage

# Runs in production on Heroku. Last stage so it's the default target for an untargeted `docker build .`
FROM base AS production

# Can be overridden at build time, e.g. by the dev stage above.
ARG UV_SYNC_ARGS="--no-dev --group production"

ENV DJANGO_SETTINGS_MODULE=apps.guide.settings.production \
    WEB_CONCURRENCY=2

# ARGs aren't available at runtime, so re-declare as an ENV to pass it through.
ARG BUILD_ENV
ENV BUILD_ENV=${BUILD_ENV}

RUN uv sync --frozen ${UV_SYNC_ARGS}

COPY --chown=guide --from=frontend-build ./apps/frontend/static ./apps/frontend/static
COPY --chown=guide . .

RUN SECRET_KEY=none python manage.py collectstatic --noinput --clear

# Gunicorn config lives in gunicorn.conf.py (its default location), which
# reads WEB_CONCURRENCY for the number of workers to spawn.
CMD ["gunicorn"]
