# syntax=docker/dockerfile:1.10
# check=error=true

# Opt into newer Dockerfile syntax, make `docker build .` fail on warnings
# See https://docs.docker.com/reference/build-checks/.
# Run `docker build --check .` for better error messages.

# NOTE: Heroku builds this file with the legacy (non-BuildKit) Docker builder:
#   - BuildKit-only features such as `RUN --mount=type=cache` aren't supported.
#   - Every stage is built, even those unused by the final stage.
# The development container is built from Dockerfile.dev instead, so this file
# only contains stages needed for production.

# frontend stages

# Keep the Node version in sync with Dockerfile.dev and .nvmrc.
FROM node:26 AS frontend-deps

# Make build & post-install scripts behave as if in CI (e.g. logging verbosity).
ARG CI=true

# Split from frontend-build so Dockerfile.dev can reuse node_modules without
# needing to run the production build.
COPY package.json package-lock.json webpack.config.js ./
RUN npm ci

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

# Use jemalloc as the system allocator: glibc's malloc fragments badly in
# long-running Python processes, so memory use creeps up over time.
# The symlink provides an architecture-independent path for LD_PRELOAD below,
# which doesn't expand globs itself. The `test -e` check fails the build if
# the glob ever stops matching: `ln -s` would otherwise silently create a
# dangling symlink, and jemalloc would not be used.
RUN apt-get update \
    && apt-get install -y --no-install-recommends libjemalloc2 \
    && rm -rf /var/lib/apt/lists/* \
    && ln -s /usr/lib/*/libjemalloc.so.2 /usr/local/lib/libjemalloc.so \
    && test -e /usr/local/lib/libjemalloc.so

ENV VIRTUAL_ENV=/venv

RUN useradd guide --create-home && mkdir /app $VIRTUAL_ENV && chown -R guide /app $VIRTUAL_ENV

WORKDIR /app

# Defaults only: any environment variables set on Heroku override these.
#  * UV_PROJECT_ENVIRONMENT - installs into $VIRTUAL_ENV instead of the
#    project's default `.venv`, so it isn't clobbered by a bind mount in dev.
#  * UV_LINK_MODE=copy - hardlinks break across Docker layers.
#  * PYTHONUNBUFFERED - otherwise logs can be lost if the process crashes:
#    https://docs.python.org/3.14/using/cmdline.html#envvar-PYTHONUNBUFFERED
#  * LD_PRELOAD / MALLOC_ARENA_MAX - use jemalloc (installed above) instead of
#    glibc's malloc, and limit the number of memory arenas glibc would
#    otherwise create per core, to keep memory use stable over time.
#  * PORT - read by Gunicorn; Heroku sets this itself and ignores EXPOSE.
ENV PATH=$VIRTUAL_ENV/bin:$PATH \
    UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    LD_PRELOAD=/usr/local/lib/libjemalloc.so \
    MALLOC_ARENA_MAX=2 \
    PORT=8000

EXPOSE 8000

# Heroku doesn't run containers as root either:
# https://devcenter.heroku.com/articles/container-registry-and-runtime#dockerfile-commands-and-runtime
USER guide

RUN python -m venv $VIRTUAL_ENV
COPY --chown=guide pyproject.toml uv.lock ./


# production stage

# Runs in production on Heroku. Last stage so it's the default target for an untargeted `docker build .`
FROM base AS production

# Can be overridden at build time, e.g. by the dev stage above.
ARG UV_SYNC_ARGS="--no-dev --group production"

ENV DJANGO_SETTINGS_MODULE=apps.guide.settings.production \
    WEB_CONCURRENCY=1

# ARGs aren't available at runtime, so re-declare as an ENV to pass it through.
ARG BUILD_ENV
ENV BUILD_ENV=${BUILD_ENV}

RUN uv sync --frozen ${UV_SYNC_ARGS}

COPY --chown=guide --from=frontend-build ./apps/frontend/static ./apps/frontend/static
COPY --chown=guide . .

RUN SECRET_KEY=none python manage.py collectstatic --noinput --clear

# Gunicorn config lives in gunicorn.conf.py (its default location), which
# reads WEB_CONCURRENCY for the number of worker processes to spawn. Requests
# are served by threads within each worker (see gunicorn.conf.py), so one
# worker process is enough to serve many concurrent requests.
CMD ["gunicorn"]
