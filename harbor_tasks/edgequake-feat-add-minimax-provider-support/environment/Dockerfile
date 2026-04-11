FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/raphaelmansuy/edgequake.git /workspace/edgequake && \
    cd /workspace/edgequake && \
    git checkout ffa9283e410ea0205be73bf3088193a34006d3d8 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/edgequake

# No extra deps needed — test_outputs.py only uses stdlib (tomllib, pathlib, re)

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
