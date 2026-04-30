FROM golang:1.25-alpine

# Install Python for test runner
RUN apk add --no-cache python3 py3-pip git bash

# Create necessary directories
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace

# Clone Hugo repository at the base commit
# Using filter=blob:none for faster cloning
RUN git init /workspace/hugo && \
    cd /workspace/hugo && \
    git remote add origin https://github.com/gohugoio/hugo.git && \
    git fetch --depth=1 origin fa8658111f9c79b3f6381273fe822854a759fe1a && \
    git checkout FETCH_HEAD

# Install Go dependencies for Hugo
WORKDIR /workspace/hugo
RUN go mod download

# Set default working directory
WORKDIR /workspace
