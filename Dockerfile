# Dockerfile for Storm
######################
# The Docker image can be built by executing:
# docker build -t yourusername/storm .
# A different base image can be set from the commandline with:
# --build-arg BASE_IMAGE=<new_base_image>
# Dockerfile installing all dependencies for Storm
##################################################
# The Docker image can be built by executing:
# docker build -t yourusername/storm-dependencies .
# A different base image can be set from the commandline with:
# --build-arg BASE_IMAGE=<new_base_image>

# Set base image
ARG BASE_IMAGE=movesrwth/storm-dependencies:latest
ARG TARGETPLATFORM

######################################################################
# Ensure we have wheels for JupyterHub and all dependencies,
# some are platform specific
#FROM $BASE_IMAGE AS wheel-builder

#ENV DEBIAN_FRONTEND=noninteractive

#
#
#RUN apt-get update -qq \
# && apt-get install -yqq --no-install-recommends \
#    build-essential \
#    ca-certificates \
#    curl \
#    locales \
#    python3-dev \
#    python3-pip \
#    python3-pycurl \
#    python3-venv  \
#    python3.13-venv
#
#WORKDIR /src/jupyterhub
#COPY requirements.txt /src/jupyterhub/
#
#
#ENV VIRTUAL_ENV=/opt/venv
#RUN python3 -m venv $VIRTUAL_ENV
#ENV PATH="$VIRTUAL_ENV/bin:$PATH"
#
#RUN python3 -m pip install --no-cache-dir --upgrade setuptools pip build wheel
#
#
#ARG PIP_CACHE_DIR=/tmp/pip-cache
#RUN --mount=type=cache,target=${PIP_CACHE_DIR} \
#    python3 -m pip wheel --wheel-dir wheelhouse -r requirements.txt


######################################################################
# The final JupyterHub image, platform specific
FROM $BASE_IMAGE AS umbihub
LABEL org.opencontainers.image.authors="dev@stormchecker.org"

#
#
#ENV DEBIAN_FRONTEND=noninteractive \
#    SHELL=/bin/bash \
#    LC_ALL=en_US.UTF-8 \
#    LANG=en_US.UTF-8 \
#    LANGUAGE=en_US.UTF-8 \
#    PYTHONDONTWRITEBYTECODE=1

EXPOSE 8000
#
#WORKDIR /srv/jupyter
#
RUN apt-get update -qq \
 && apt-get install -yqq --no-install-recommends \
#    ca-certificates \
#    curl \
#    gnupg \
#    locales \
    python-is-python3 \
    python3-pip \
#    python3-pycurl \
    python3-venv
#    nodejs \
#    npm \
# && locale-gen $LC_ALL \
# && npm install -g configurable-http-proxy@^4.6.2 \
# # clean cache and logs
# && rm -rf /var/lib/apt/lists/* /var/log/* /var/tmp/* ~/.npm
#
ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN python3 -m pip install  --no-cache-dir  jupyter matplotlib scipy


#
# CMake build type
ARG storm_build_type=Release
# Specify number of threads to use for parallel compilation
ARG no_threads=1
#
# For storm: libarchive-dev and ninja-build
# For prism: default-jdk
RUN apt-get update -qq \
 && apt-get install -yqq --no-install-recommends \
    libarchive-dev ninja-build libboost-iostreams-dev \
    default-jdk



# Build Storm
#############
WORKDIR /opt/

RUN git clone  -b io/binaryformat https://github.com/tquatmann/storm.git

# Switch to build directory
RUN mkdir -p /opt/storm/build
WORKDIR /opt/storm/build

# Configure Storm
RUN cmake -GNinja -DCMAKE_BUILD_TYPE=$storm_build_type \
          -DSTORM_PORTABLE=ON \
          -DSTORM_USE_LTO=OFF \
          -DSTORM_DEVELOPER=ON ..
RUN ninja storm-cli -j 4

WORKDIR /opt/

RUN git clone -b umb https://github.com/davexparker/prism.git
WORKDIR /opt/prism/prism
RUN make

#############
RUN mkdir /opt/umb
WORKDIR /opt/umb

RUN python3 -m pip install  --no-cache-dir  umbi

# Copy the content of the current local repository into the Docker image
COPY . .

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8000", "--no-browser", "--allow-root"]