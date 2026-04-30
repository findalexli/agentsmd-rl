FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/mlflow/mlflow.git /workspace/mlflow && \
    cd /workspace/mlflow && \
    git checkout 956ab37d911e777ce40740ab851d2d472cec2752 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/mlflow

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
