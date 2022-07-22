# Guide

Guide is a website to help content editors, moderators, administrators, and other users learn how to user the Wagtail content management system (CMS).

The Wagtail guide will ultimately include:
- Tutorials 
- How-to articles
- Reference materials
- Walkthroughs and visual learning materials

# Document contents

- [Installation](#installation)
- [Contributing](#contributing)
- [Other Notes](#other-notes)

# Installation

## Development

We assume that you have basic knowledge of Node/Yarn/Webpack and Python/Django/Wagtail.

- [Venv](#setup-with-venv)
- [Gitpod](#setup-with-gitpod)


## Setup with Venv

You can run Wagtail Guide locally on your machine using Virtualenv.

#### Dependencies
- Python 3.9
- Git
- Node 16.*
- [Yarn](https://yarnpkg.com/)

### Installation

With [PIP](https://github.com/pypa/pip) installed, run:

    python -V

Confirm that the output is showing version Python 3.9. If not, you may have multiple versions of python installed on your system and will need to switch to the appropriate version when creating the virtual environment.

With the Python 3.9 output confirmed, run:

    python -m venv env
    source env/bin/activate

Now we're ready to set up the guide project:

    cd ~/dev [or your preferred dev directory]
    git clone https://github.com/wagtail/guide.git
    cd guide
    make backend
    make frontend
    make buildfixtures

Once the backend and frontend have been set up, you can run the development server with:

    make run

If everything worked, [http://127.0.0.1:8000](http://127.0.0.1:8000) should show you a welcome page.

You can access the administrative area at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin) and log in using the credentials you created during the backend setup. 

## Setup with Gitpod

Launch a ready-to-code Wagtail Guide development environment with a single click.

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/wagtail/guide)

Steps:

1. Click the ``Open in Gitpod`` button.
2. Relax: a development environment with an active Wagtail Guide site will be created for you.
3. Login at `/admin/` with username `admin` and password `changeme`


# Contributing

If you're a python or Django developer, fork the repo and join us. You'll find answers to many common new contributor questions in our [contributing guidelines](https://github.com/wagtail/bakerydemo/blob/master/contributing.md).

# Other Notes

## Google Summer of Code

This project is a part of Google Summer of Code 2022 under the organization [**Wagtail**](https://wagtail.org/). Find more details about the project [here](https://summerofcode.withgoogle.com/programs/2022/projects/7nMw2hTq).

