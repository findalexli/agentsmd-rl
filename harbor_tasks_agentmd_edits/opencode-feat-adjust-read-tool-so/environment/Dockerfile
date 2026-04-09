FROM golang:1.24

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/opencode-ai/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout 170c7ad67abd840fd89aef3c79b5eff32e3aec5c && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Pre-fetch Go dependencies for faster builds
RUN go mod download && go build ./... 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
