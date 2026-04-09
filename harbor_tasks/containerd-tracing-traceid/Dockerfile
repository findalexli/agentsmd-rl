# Build stage
FROM golang:1.23-alpine AS builder

RUN apk add --no-cache git make

# Clone the containerd repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/containerd/containerd.git containerd && \
    cd containerd && \
    git checkout ae04fbd2e11a28b32b184024b4ed397713d642d7

# Install Python for the test runner
FROM python:3.12-alpine

RUN apk add --no-cache git go bash

# Copy the repository
COPY --from=builder /workspace/containerd /workspace/containerd

# Install pytest
RUN pip install pytest

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/containerd
