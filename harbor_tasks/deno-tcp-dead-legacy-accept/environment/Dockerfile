FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/denoland/deno.git /workspace/deno && \
    cd /workspace/deno && \
    git checkout ad725eea313df6204d342d84ace4af1b11cc341f && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/deno

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
