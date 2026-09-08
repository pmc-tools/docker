# Dockerfile for UMB Obervatory
# Based on the Storm docker files.

# Set base image.
# We use the prebuilt Storm image, which already contains a current Storm
# snapshot (with UMB support) at /usr/local/bin/storm, instead of building
# Storm from source (which used to take very long).
ARG BASE_IMAGE=movesrwth/storm:ci


######################################################################
# The final JupyterHub image, platform specific
FROM $BASE_IMAGE AS umbiobservatory
LABEL org.opencontainers.image.authors="pmctools"

ARG TARGETPLATFORM
EXPOSE 8000

# Build dependencies for the remaining tools
# For prism: default-jdk, ninja-build, xz-utils; for modest: xz-utils
RUN apt-get update -qq \
 && apt-get install -yqq --no-install-recommends \
    python-is-python3 \
    python3-pip \
    python3-venv \
    unzip \
    ninja-build libboost-iostreams-dev \
    default-jdk  \
    xz-utils

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m pip install  --no-cache-dir  jupyter jupytext matplotlib scipy pytest

#
# Build Prism
#############
ARG prism_repo=https://github.com/davexparker/prism.git
ARG prism_branch=umb

WORKDIR /opt/
RUN git clone -b $prism_branch $prism_repo
WORKDIR /opt/prism/prism
RUN make

# Download Modest
#################
WORKDIR /opt/
COPY .docker/install-modest.sh install-modest.sh
RUN bash install-modest.sh

# Verify that Storm is available
RUN storm --version

#### Install UMB
RUN python3 -m pip install --no-cache-dir  umbi

#############
RUN mkdir /opt/umb
WORKDIR /opt/umb

# Copy the content of the current local repository into the Docker image
COPY . .
# The notebook sources live in markdown; materialize the .ipynb the Jupyter
# server will serve from the paired text representation.
RUN jupytext --to ipynb getting_started.md
COPY .docker/tools.toml tools.toml

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8000", "--no-browser", "--allow-root"]
