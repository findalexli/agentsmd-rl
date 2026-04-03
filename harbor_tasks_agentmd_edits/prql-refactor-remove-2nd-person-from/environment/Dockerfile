FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/PRQL/prql.git /workspace/prql && \
    cd /workspace/prql && \
    git checkout efff1bad5f42a6f6cdd10514502028fe41b75db4 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/prql

# No Rust toolchain needed — tests check source file content only
# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
