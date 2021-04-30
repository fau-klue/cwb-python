FROM ubuntu:20.04

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
    cython3 \
    less \
    mg


# Download latest cwb source
RUN svn co http://svn.code.sf.net/p/cwb/code/cwb/trunk /cwb

# Set installation directory to standard (/usr/local tree) and run install script 
WORKDIR /cwb
RUN sed -i 's/SITE=beta-install/SITE=standard/' config.mk
RUN ./install-scripts/install-linux

# Compile
COPY . /cwb-python
WORKDIR /cwb-python
RUN python3 setup.py build_ext --inplace
