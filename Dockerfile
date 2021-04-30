FROM martialblog/docker-corpus-tool:cwb-ucs
LABEL maintainer="markus.opolka@fau.de"

RUN set -ex; \
        apt-get update && \
        apt-get install --no-install-recommends -y \
        \
        gcc \
        libglib2.0-0 \
        libglib2.0-dev \
        python3 \
        python3-dev \
        python3-setuptools \
        cython3

COPY . /src
WORKDIR /src

# Compile
RUN python3 setup.py build_ext --inplace
