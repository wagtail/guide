# (Keep the version in sync with the node install below)
FROM node:24 as frontend

# Make build & post-install scripts behave as if we were in a CI environment (e.g. for logging verbosity purposes).
ARG CI=true

# Install front-end dependencies.
COPY package.json package-lock.json webpack.config.js ./
RUN npm ci

# Compile static files
COPY ./apps/frontend/static_src/ ./apps/frontend/static_src/
RUN npm run build


# We use Debian images because they are considered more stable than the alpine
# ones becase they use a different C compiler. Debian images also come with
# all useful packages required for image manipulation out of the box. They
# however weigh a lot, approx. up to 1.5GiB per built image.
FROM python:3.14 as production

# Install uv using the official standalone binary.
# Keep this version in sync with the local `uv` used to generate uv.lock.
COPY --from=ghcr.io/astral-sh/uv:0.11.19 /uv /uvx /bin/

# Arguments to control which dependency groups get installed. Defaults to the
# production configuration, and can be overridden at build time (e.g. for the
# development container).
ARG UV_SYNC_ARGS="--no-dev --group production"

# Install dependencies in a virtualenv
ENV VIRTUAL_ENV=/venv

RUN useradd guide --create-home && mkdir /app $VIRTUAL_ENV && chown -R guide /app $VIRTUAL_ENV

WORKDIR /app

# Set default environment variables. They are used at build time and runtime.
# If you specify your own environment variables on Heroku, they will
# override the ones set here. The ones below serve as sane defaults only.
#  * PATH - Make sure that uv is on the PATH, along with our venv
#  * UV_PROJECT_ENVIRONMENT - Install dependencies into $VIRTUAL_ENV instead of
#    the default `.venv` in the project directory.
#  * UV_COMPILE_BYTECODE - Compile Python bytecode for faster container starts.
#  * UV_LINK_MODE - Use copy mode to avoid hardlinks which break in Docker layers.
#  * PYTHONUNBUFFERED - This is useful so Python does not hold any messages
#    from being output.
#    https://docs.python.org/3.14/using/cmdline.html#envvar-PYTHONUNBUFFERED
#    https://docs.python.org/3.14/using/cmdline.html#cmdoption-u
#  * DJANGO_SETTINGS_MODULE - default settings used in the container.
#  * PORT - default port used. Please match with EXPOSE.
#    Heroku will ignore EXPOSE and only set PORT variable. PORT variable is
#    read/used by Gunicorn.
#  * WEB_CONCURRENCY - number of workers used by Gunicorn. The variable is
#    read by Gunicorn.
ENV PATH=$VIRTUAL_ENV/bin:$PATH \
    UV_PROJECT_ENVIRONMENT=$VIRTUAL_ENV \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=apps.guide.settings.production \
    PORT=8000 \
    WEB_CONCURRENCY=2

# Make $BUILD_ENV available at runtime
ARG BUILD_ENV
ENV BUILD_ENV=${BUILD_ENV}

# Port exposed by this container. Should default to the port used by your WSGI
# server (Gunicorn). Heroku will ignore this.
EXPOSE 8000

# Don't use the root user as it's an anti-pattern and Heroku does not run
# containers as root either.
# https://devcenter.heroku.com/articles/container-registry-and-runtime#dockerfile-commands-and-runtime
USER guide

# Install your app's Python requirements.
RUN python -m venv $VIRTUAL_ENV
COPY --chown=guide pyproject.toml uv.lock ./
RUN uv sync --frozen ${UV_SYNC_ARGS}

COPY --chown=guide --from=frontend ./apps/frontend/static ./apps/frontend/static

# Copy application code.
COPY --chown=guide . .

# Collect static. This command will move static files from application
# directories and "static_compiled" folder to the main static directory that
# will be served by the WSGI server.
RUN SECRET_KEY=none python manage.py collectstatic --noinput --clear

# Run the WSGI server. Configuration lives in `gunicorn.conf.py`, which
# configures the app, port and worker recycling. `WEB_CONCURRENCY` is read by
# gunicorn to determine the number of workers.
CMD gunicorn
