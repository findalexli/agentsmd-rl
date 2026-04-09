FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux unzip && \
    rm -rf /var/lib/apt/lists/*

# Install Deno (needed to execute TypeScript tests)
RUN curl -fsSL https://deno.land/install.sh | DENO_INSTALL=/usr/local sh

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/denoland/deno.git /workspace/deno && \
    cd /workspace/deno && \
    git checkout 6710d587bc05e4275c2336fb1cc5104d5eee9fdc && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/deno

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
