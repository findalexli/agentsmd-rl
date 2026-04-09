FROM golang:1.25-alpine

RUN apk add --no-cache git python3 py3-pip bash

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create log directory
RUN mkdir -p /logs/verifier

# Clone containerd repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/containerd/containerd.git && \
    cd containerd && \
    git checkout 18201e7d52037a8a9657a2764ef63f60ec556e37

WORKDIR /workspace/containerd

# Download dependencies
RUN go mod download

# Copy test files
COPY tests/test_outputs.py /workspace/tests/
COPY tests/new_tests.go /workspace/tests/
COPY solution/solve.sh /workspace/solution/
RUN chmod +x /workspace/solution/solve.sh
