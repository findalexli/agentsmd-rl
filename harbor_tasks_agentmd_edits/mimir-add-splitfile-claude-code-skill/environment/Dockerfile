FROM golang:1.23-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow — mimir is large)
RUN git init /workspace/mimir && \
    cd /workspace/mimir && \
    git remote add origin https://github.com/grafana/mimir.git && \
    git fetch --depth=1 origin 0de2c7d947b81573a2c13bf4b931f9a2a04891ec && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/mimir

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
