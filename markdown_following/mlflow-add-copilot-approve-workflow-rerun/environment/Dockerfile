FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git init /workspace/mlflow && \
    cd /workspace/mlflow && \
    git remote add origin https://github.com/mlflow/mlflow.git && \
    git fetch --depth=1 origin 39f35acce9e63788371bfaaa2c57cafef10a02ec && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/mlflow

# Verifier output directory
RUN mkdir -p /logs/verifier

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
