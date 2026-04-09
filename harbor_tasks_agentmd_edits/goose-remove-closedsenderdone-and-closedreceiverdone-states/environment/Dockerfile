FROM golang:1.23-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/goose-lang/goose.git /workspace/goose && \
    cd /workspace/goose && \
    git checkout 16144157af4b64fe96deac36fcd2638503fdc2e2 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/goose

# Pre-fetch Go module dependencies for faster test execution
RUN go mod download 2>/dev/null || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
