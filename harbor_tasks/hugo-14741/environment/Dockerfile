FROM golang:1.24-alpine

RUN apk add --no-cache git python3 py3-pip bash

WORKDIR /workspace

# Clone Hugo repository at base commit
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git hugo && \
    cd hugo && \
    git checkout 161d0d475773c5251ec00cc8848f1a174393155c

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/hugo
