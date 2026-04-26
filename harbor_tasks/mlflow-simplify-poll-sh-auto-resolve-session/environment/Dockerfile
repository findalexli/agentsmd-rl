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
    git fetch --depth=1 origin cd2cea0d7acf7d47f4fbd8f94e7da0844a89e76a && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/mlflow

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
