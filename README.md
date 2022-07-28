# Guide

Guide is a website to help content editors, moderators, administrators, and other users learn how to user the Wagtail content management system (CMS).

The Wagtail guide will ultimately include:
- Tutorials 
- How-to articles
- Reference materials
- Walkthroughs and visual learning materials

You can learn more about the documentation system [here](https://documentation.divio.com/).

# Table of Contents

- [Installation](#installation)
- [Gitpod](#gitpod)
- [Contributing](#contributing)
- [Other Notes](#other-notes)

# Installation

We assume that you have basic knowledge of Node/Yarn/Webpack and Python/Django/Wagtail in these instructions. We recommend you develop Wagtail Guide locally on your machine using venv.

#### Dependencies
- Python 3.9
- Git
- Node 16.*
- [Yarn](https://yarnpkg.com/)

### Setting up Wagtail guide in a virtual environment

Run:

    python -V

Confirm that the output is showing version Python 3.9. If not, you may have multiple versions of Python installed on your system and will need to switch to the appropriate version when creating the virtual environment.

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

With Gitpod you can deploy a ready-to-code Wagtail Guide development environment with a single click to evaluate the code.

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/wagtail/guide)

Steps:

1. Click the ``Open in Gitpod`` button.
2. Relax: a development environment with an active Wagtail Guide site will be created for you.
3. Login at `/admin/` with username `admin` and password `changeme`


# Contributing

If you're a Python or Django developer, fork the repo and join us. You'll find answers to many common new contributor questions in our [contributing guidelines](https://docs.wagtail.org/en/stable/contributing/index.html).

# Other Notes

## Google Summer of Code

This project is one of three [Wagtail](https://wagtail.org/) projects being sponsored by Google as a part of [Google Summer of Code 2022](https://summerofcode.withgoogle.com/). The team for this project includes:

### Contributor

- [Hitansh Shah](https://github.com/Hitansh-Shah)

### Mentors

- [Phil Dexter](https://github.com/phildexter)
- [Coen van der Kamp](https://github.com/allcaps)
- [Meagen Voss](https://github.com/vossisboss)


You can learn more about our Google Summer of Code projects in this [blog](https://wagtail.org/blog/wagtail-cms-projects-for-google-summer-of-code-2022/) or on our [wiki page](https://github.com/wagtail/wagtail/wiki/Google-Summer-of-Code-2022).
