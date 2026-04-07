FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        python3 python3-pip python3-venv \
        libdbus-1-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/block/goose.git /workspace/goose && \
    cd /workspace/goose && \
    git checkout 948cb91d5402b6175d4ff6386e8e02beea6b86cd && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/goose

RUN mkdir -p /logs/verifier
