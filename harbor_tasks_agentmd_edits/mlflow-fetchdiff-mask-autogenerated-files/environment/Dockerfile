FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/mlflow/mlflow.git /workspace/mlflow && \
    cd /workspace/mlflow && \
    git checkout 33200f3a6208bee42c5c1c10a4687bc78302b9a8 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/mlflow

RUN pip install --no-cache-dir pytest pytest-json-ctrf

RUN mkdir -p /logs/verifier
