FROM golang:1.23-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/hugo && \
    cd /workspace/hugo && \
    git remote add origin https://github.com/gohugoio/hugo.git && \
    git fetch --depth=1 origin b55d452e46e81369a65978459a0683efa484c11b && \
    git checkout FETCH_HEAD

WORKDIR /workspace/hugo

# Pre-fetch Go module dependencies
RUN go mod download

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
