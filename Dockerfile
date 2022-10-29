# (Keep the version in sync with the node install below)
FROM node:16 as frontend

# Make build & post-install scripts behave as if we were in a CI environment (e.g. for logging verbosity purposes).
ARG CI=true

# Install front-end dependencies.
COPY package.json package-lock.json webpack.config.js ./
RUN npm ci

# Compile static files
COPY ./apps/frontend/static_src/ ./apps/frontend/static_src/
RUN npm run build

# We use Debian images because they are considered more stable than the alpine
# ones because they use a different C compiler. Debian images also come with
# all useful packages required for image manipulation out of the box. They
# however weigh a lot, approx. up to 1.5GiB per built image.
FROM python:3.9 as production

# Install dependency needed to run guide init script
RUN apt-get update && apt-get install -y gettext  

ARG POETRY_HOME=/opt/poetry
ARG POETRY_INSTALL_ARGS="--without dev"

# IMPORTANT: Remember to review this when upgrading
ARG POETRY_VERSION=1.2.2

# Install dependencies in a virtualenv
ENV VIRTUAL_ENV=/venv

RUN useradd guide --create-home && mkdir /app $VIRTUAL_ENV && chown -R guide /app $VIRTUAL_ENV

WORKDIR /app

# Set default environment variables. They are used at build time and runtime.
# If you specify your own environment variables on Heroku, they will
# override the ones set here. The ones below serve as sane defaults only.
#  * PATH - Make sure that Poetry is on the PATH, along with our venv
#  * PYTHONUNBUFFERED - This is useful so Python does not hold any messages
#    from being output.
#    https://docs.python.org/3.9/using/cmdline.html#envvar-PYTHONUNBUFFERED
#    https://docs.python.org/3.9/using/cmdline.html#cmdoption-u
#  * DJANGO_SETTINGS_MODULE - default settings used in the container.
#  * PORT - default port used. Please match with EXPOSE.
#    Heroku will ignore EXPOSE and only set PORT variable. PORT variable is
#    read/used by Gunicorn.
#  * WEB_CONCURRENCY - number of workers used by Gunicorn. The variable is
#    read by Gunicorn.
#  * GUNICORN_CMD_ARGS - additional arguments to be passed to Gunicorn. This
#    variable is read by Gunicorn
ENV PATH=${POETRY_HOME}/bin:$VIRTUAL_ENV/bin:$PATH \
    POETRY_INSTALL_ARGS=${POETRY_INSTALL_ARGS} \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=apps.guide.settings.production \
    PORT=8000 \
    WEB_CONCURRENCY=3 \
    GUNICORN_CMD_ARGS="-c gunicorn-conf.py --max-requests 1200 --max-requests-jitter 50 --access-logfile - --timeout 25"

# Make $BUILD_ENV available at runtime
ARG BUILD_ENV
ENV BUILD_ENV=${BUILD_ENV}

# Port exposed by this container. Should default to the port used by your WSGI
# server (Gunicorn). Heroku will ignore this.
EXPOSE 8000

# Install poetry using the installer (keeps Poetry's dependencies isolated from the app's)
# chown protects us against cases where files downloaded by poetry have invalid ownership
# chmod ensures poetry dependencies are accessible when packages are installed
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN chown -R root:root ${POETRY_HOME} && \
    chmod -R 0755 ${POETRY_HOME}

# Don't use the root user as it's an anti-pattern and Heroku does not run
# containers as root either.
# https://devcenter.heroku.com/articles/container-registry-and-runtime#dockerfile-commands-and-runtime
USER guide

# Install your app's Python requirements.
RUN python -m venv $VIRTUAL_ENV
COPY --chown=guide pyproject.toml poetry.lock ./
RUN pip install --upgrade pip && poetry install ${POETRY_INSTALL_ARGS} --no-root

COPY --chown=guide --from=frontend ./apps/frontend/static ./apps/frontend/static

# Copy application code.
COPY --chown=guide . .

RUN poetry install ${POETRY_INSTALL_ARGS}

# Collect static. This command will move static files from application
# directories and "static_compiled" folder to the main static directory that
# will be served by the WSGI server.
RUN SECRET_KEY=none python manage.py collectstatic --noinput --clear

# Run the WSGI server. It reads GUNICORN_CMD_ARGS, PORT and WEB_CONCURRENCY
# environment variable hence we don't specify a lot options below.
CMD gunicorn apps.guide.wsgi:application
