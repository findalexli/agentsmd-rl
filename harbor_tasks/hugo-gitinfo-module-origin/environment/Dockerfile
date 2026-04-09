FROM golang:1.25-alpine

# Install Python, git, and other dependencies needed for testing
RUN apk add --no-cache python3 py3-pip py3-pytest git bash

# Allow pip to install packages in system Python (needed for test.sh)
ENV PIP_BREAK_SYSTEM_PACKAGES=1

# Set up working directory
WORKDIR /workspace

# Clone Hugo repo at base commit (before the fix)
ARG BASE_COMMIT=68059972e8789258447e31ca23641c79598d66be
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git hugo && \
    cd hugo && \
    git checkout ${BASE_COMMIT}

# Pre-download Go modules to speed up testing
RUN cd /workspace/hugo && go mod download

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

WORKDIR /workspace/hugo
