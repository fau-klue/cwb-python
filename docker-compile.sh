#!/usr/bin/env bash
# Script to compile Cython code using a Docker image with the Corpus Workbench installed

set -x

# Remove any existing container
if [ "$(docker container list -a | grep cwb-artifact)" ]; then
    docker container rm cwb-artifact
fi

# Build image to create build artifacts
docker build -t cwb-python .

# Create container containing build artifacts
docker create --name cwb-artifact cwb-python

# Copy build artifacts to local directory
docker cp cwb-artifact:/src/cwb_python/CWB/CL.c ./cwb_python/CWB/
docker cp cwb-artifact:/src/cwb_python/CWB/CL.h ./cwb_python/CWB/

# Docker cp does not support globbing/wildcards yet
docker cp cwb-artifact:/src/cwb_python/CWB/CL.cpython-35m-x86_64-linux-gnu.so ./cwb_python/CWB/ || echo 0
docker cp cwb-artifact:/src/cwb_python/CWB/CL.cpython-36m-x86_64-linux-gnu.so ./cwb_python/CWB/ || echo 0
