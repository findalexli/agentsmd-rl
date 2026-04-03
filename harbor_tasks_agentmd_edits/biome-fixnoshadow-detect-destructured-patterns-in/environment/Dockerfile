FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (shallow: biome is a large Rust monorepo)
RUN git init /workspace/biome && \
    cd /workspace/biome && \
    git remote add origin https://github.com/biomejs/biome.git && \
    git fetch --depth=1 origin 4509fc654f90cc007689c9e46bc3d172016ae039 && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/biome

# No compilation needed — tests check file content and test spec structure
# (biome is a huge Rust project, compilation would be impractical in test container)

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
