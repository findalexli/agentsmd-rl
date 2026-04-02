FROM golang:1.24-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/gohugoio/hugo.git /workspace/hugo && \
    cd /workspace/hugo && \
    git checkout b55d452e46e81369a65978459a0683efa484c11b && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/hugo

# Pre-fetch Go module dependencies
RUN go mod download

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
