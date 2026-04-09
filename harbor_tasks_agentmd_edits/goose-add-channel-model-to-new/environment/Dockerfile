FROM golang:1.23-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/goose-lang/goose.git /workspace/goose && \
    cd /workspace/goose && \
    git checkout 3be88bbb4982f58e5813b6f0344302d5582c8e8a && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/goose

# Initialize go module and pre-fetch common deps
RUN go mod tidy 2>/dev/null || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
