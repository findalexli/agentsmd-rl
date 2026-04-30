FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux \
        python3 python3-pip python3-venv \
        libdbus-1-dev pkg-config && \
    rm -rf /var/lib/apt/lists/*

RUN git init /workspace/goose && \
    cd /workspace/goose && \
    git remote add origin https://github.com/block/goose.git && \
    git fetch --depth=1 origin 948cb91d5402b6175d4ff6386e8e02beea6b86cd && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/goose

RUN mkdir -p /logs/verifier
