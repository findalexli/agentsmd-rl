FROM golang:1.26-alpine

ENV LANG=C.UTF-8

RUN apk add --no-cache git curl ca-certificates build-base bash python3 py3-pip

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/goose-lang/goose.git /workspace/goose && \
    cd /workspace/goose && \
    git checkout e0f62c9e03d8be7f5cd4ed95347b8c23d3c34212 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/goose

# Pre-fetch Go dependencies for faster agent builds
RUN go mod download

# Install Python dependencies for test runner
RUN pip3 install --break-system-packages pytest

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
