FROM golang:1.25-alpine

# Install Python for the test runner
RUN apk add --no-cache python3 py3-pip py3-pytest git patch bash

# Create necessary directories
RUN mkdir -p /logs/verifier

# Clone Hugo repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git hugo && \
    cd hugo && \
    git checkout 87f8de8c7ab10516614180080f97490645bbfdec

WORKDIR /workspace/hugo

# Download Go module dependencies
RUN go mod download

# Pre-build to cache dependencies
RUN go build -o /dev/null ./... 2>/dev/null || true
