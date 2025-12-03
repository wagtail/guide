FROM gitpod/workspace-full

RUN sudo apt-get update && sudo rm -rf /var/lib/apt/lists/*

ARG PYTHON_VERSION=3.14.6
RUN pyenv install ${PYTHON_VERSION} && pyenv global ${PYTHON_VERSION}
