# Wagtail user guide

The user guide is a website to help content editors, moderators, administrators, and other users learn how to use the Wagtail content management system (CMS). It’s a comprehensive documentation resource for CMS users, featuring hands-on learning material as well as reference content. It follows the [Diátaxis](https://diataxis.fr/) framework. For the Wagtail developer documentation, visit [docs.wagtail.org](https://docs.wagtail.org/en/stable/).

The Wagtail guide will ultimately include:

- Tutorials
- How-to articles
- Reference materials
- Walkthroughs and visual learning materials

You can learn more about the documentation system [here](https://documentation.divio.com/).

# Table of Contents

- [Installation](#installation)
- [Contributing](#contributing)
- [Other Notes](#other-notes)

# Installation

We assume that you have basic knowledge of Node/Webpack and Python/Django/Wagtail in these instructions. We recommend you develop Wagtail Guide locally on your machine using `venv` and [fnm](https://github.com/Schniz/fnm) to ensure you are on the correct Node version.

#### Dependencies

- Git
- Python >= 3.14
- uv
- just
- Node (see `.nvmrc` for version)

### Setting up Wagtail guide in a virtual environment

Run:

    python -V

Confirm that the output is showing version Python 3.14 (or higher). If not, you may have multiple versions of Python installed on your system and will need to switch to the appropriate version when creating the virtual environment.

With the Python version output confirmed, [install uv](https://docs.astral.sh/uv/).

Now we're ready to set up the guide project:

    cd ~/dev [or your preferred dev directory]
    git clone https://github.com/wagtail/guide.git
    cd guide
    just backend
    just frontend
    just buildfixtures

Once the backend and frontend have been set up, you can run the development server with:

    just run

If everything worked, [http://127.0.0.1:8000](http://127.0.0.1:8000) should show you a welcome page.

You can access the administrative area at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) and log in using the credentials you created during the backend setup.

`uv` manages the project's virtual environment automatically, so there's no need to activate it manually. To run a command in the environment, prefix it with `uv run`, for example `uv run python manage.py shell`.

To generate and compile translation strings, run:

    just makemessages
    just compilemessages

Or both, in a single command:

    just translations

### Setting up development with Docker

1. Optionally, create a `.env` file in the project root containing these variables, you can adjust the values to your preferences:
    ```
    ALLOWED_HOSTS=localhost
    PORT=8000
    SECRET_KEY=some-random-secret
    DJANGO_SETTINGS_MODULE=apps.guide.settings.dev
    ```
2. Build and start the development container by running `docker compose up --remove-orphans`.
   This starts the server in the foreground. To run it in the background, add `-d`.
3. In another terminal, open a shell in the container: `docker compose exec web bash`
4. From that shell, run `just backend` to set up the database, and `just frontend` to build the
   front-end assets. The container bundles Python and Node, so any other `just` recipe (`just
test`, `just lint`, ...) works the same as it does on the host — you don't need either
   installed locally to use Docker.
5. You should now have access to the project in your browser at `http://localhost:8000`
6. To stop the container, run `docker compose down`

Code changes are picked up automatically. Only rebuild the image when dependencies change: `docker compose build`.

# Contributing

If you're a Python or Django developer, fork the repo and join us. You'll find answers to many common new contributor questions in our [contributing guidelines](https://docs.wagtail.org/en/stable/contributing/index.html).

## Development

- Run formatting (Ruff & Prettier) `just format`
- Run linting (Ruff, Prettier, Eslint) `just lint`
- Run tests `just test`

# Other Notes

## Google Summer of Code

This project is one of three [Wagtail](https://wagtail.org/) projects being sponsored by Google as a part of [Google Summer of Code 2022](https://summerofcode.withgoogle.com/). The team for this project includes:

### Contributor

- [Hitansh Shah](https://github.com/Hitansh-Shah)

### Mentors

- [Thibaud Colas](https://github.com/thibaudcolas)
- [Coen van der Kamp](https://github.com/allcaps)
- [Meagen Voss](https://github.com/vossisboss)

You can learn more about our Google Summer of Code project in [Google Summer of Code: Wagtail Editor Guide](https://wagtail.org/blog/google-summer-of-code-wagtail-editor-guide/), [Wagtail CMS projects for Google Summer of Code 2022](https://wagtail.org/blog/wagtail-cms-projects-for-google-summer-of-code-2022/) or on our [wiki page](https://github.com/wagtail/wagtail/wiki/Google-Summer-of-Code-2022).
