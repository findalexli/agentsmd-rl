FROM rust:1.85-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/biomejs/biome.git /workspace/biome && \
    cd /workspace/biome && \
    git checkout 716e4e195d6a76f02850f3cf41b8b38b757708ec && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/biome

# Pre-compile dependencies for biome_markdown_parser to speed up subsequent builds.
# We use cargo check (not build/test) to verify the code compiles, then delete
# the target directory to keep the image small - tests will compile fresh when run.
RUN cargo check -p biome_markdown_parser 2>&1 && rm -rf target

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
