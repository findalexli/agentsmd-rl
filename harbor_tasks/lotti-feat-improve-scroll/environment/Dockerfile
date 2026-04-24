FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/matthiasn/lotti.git /workspace/lotti && \
    cd /workspace/lotti && \
    git checkout fda7c15b3cd6b88a3d9d258d458ce202f4b025c8 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/lotti

RUN mkdir -p /logs/verifier

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages black flake8 isort 2>/dev/null || pip install --no-cache-dir black flake8 isort
