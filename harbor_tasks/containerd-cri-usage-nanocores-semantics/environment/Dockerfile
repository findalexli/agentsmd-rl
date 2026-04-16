FROM golang:1.25-alpine

# Install git, python, and other dependencies
RUN apk add --no-cache git make bash curl python3 py3-pip

# Clone containerd at the base commit
ARG BASE_COMMIT=b7a467e4f3a46c4b13d5fac5a4206738d6ee2883
RUN git clone --filter=blob:none https://github.com/containerd/containerd.git /workspace/containerd && \
    cd /workspace/containerd && \
    git checkout ${BASE_COMMIT}

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/containerd
