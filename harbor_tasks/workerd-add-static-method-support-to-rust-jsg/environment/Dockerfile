FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (sparse checkout — only fetch files needed for tests)
RUN git init /workspace/workerd && \
    cd /workspace/workerd && \
    git remote add origin https://github.com/cloudflare/workerd.git && \
    git fetch --depth=1 origin d7dc27c438f7ea1fd5eb28a0258d5dbae265a99d && \
    git checkout FETCH_HEAD \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/workerd

# Install rustfmt for syntax checking
RUN rustup component add rustfmt

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
