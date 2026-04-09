# syntax=docker/dockerfile:1
FROM golang:1.23-alpine

# Install git and Python for testing
RUN apk add --no-cache git python3 py3-pip bash

WORKDIR /workspace

# Clone Hugo repo at the base commit
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git hugo && \
    cd hugo && \
    git checkout dc9b51d2e2fa1bfc2b7c68c01417bb7ae2c9c6a2

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/hugo
