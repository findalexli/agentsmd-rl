FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (pre-fix)
RUN git clone --filter=blob:none https://github.com/matthiasn/lotti.git /workspace/lotti && \
    cd /workspace/lotti && \
    git checkout 5cb0c3b44893b5e81abd677aeb74692bb66b2138 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lotti

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
