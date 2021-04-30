FROM ubuntu:20.04 as builder

# install cwb dependencies
RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive \
    apt-get install --no-install-recommends -y \
    apt-utils \
    autoconf \
    bison \
    flex \
    gcc \
    libc6-dev \
    libglib2.0-0 \
    libglib2.0-dev \
    libncurses5 \
    libncurses5-dev \
    libpcre3-dev \
    libreadline8 \
    libreadline-dev \
    make \
    pkg-config \
    subversion \
    python3 \
    python3-dev \
    python3-setuptools \
    cython3


# Download latest cwb source
RUN svn co http://svn.code.sf.net/p/cwb/code/cwb/trunk /cwb

# Run install script and Move to unified location
WORKDIR /cwb
RUN ./install-scripts/install-linux
RUN mv /usr/local/cwb-* /usr/local/cwb

# Copy all files
COPY . /src
WORKDIR /src

# Compile
RUN python3 setup.py build_ext --inplace
