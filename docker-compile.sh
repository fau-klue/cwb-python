#!/usr/bin/env bash
# Script to compile Cython code using a Docker image with the Corpus Workbench installed

set -ex

# Remove any existing container
docker container rm -f cwb-artifact

# Build image to create build artifacts
docker build -t cwb-python .

# Create container containing build artifacts
docker create --name cwb-artifact cwb-python

# Copy build artifacts to local directory
docker cp cwb-artifact:/src/cwb_python/CWB/CL.c ./cwb_python/CWB/
docker cp cwb-artifact:/src/cwb_python/CWB/CL.h ./cwb_python/CWB/
docker cp cwb-artifact:/src/cwb_python/CWB/CL.cpython-35m-x86_64-linux-gnu.so ./cwb_python/CWB/
