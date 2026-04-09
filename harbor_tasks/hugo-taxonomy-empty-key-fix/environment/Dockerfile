FROM golang:1.23-alpine

WORKDIR /workspace

# Install required tools
RUN apk add --no-cache git python3 py3-pip bash

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Clone Hugo repository at base commit (before fix)
ENV REPO_URL=https://github.com/gohugoio/hugo.git
ENV BASE_COMMIT=cc338a9d4854c7e7273a5c3c8fee436c642f4dde
RUN git clone --filter=blob:none $REPO_URL hugo && \
    cd hugo && \
    git checkout $BASE_COMMIT

# Install Python dependencies for tests
RUN pip3 install --break-system-packages pytest pyyaml

# Set Go toolchain to auto to handle version requirements
ENV GOTOOLCHAIN=auto

WORKDIR /workspace/hugo
