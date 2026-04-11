FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --filter=blob:none https://github.com/mlflow/mlflow.git /workspace/mlflow && \
    cd /workspace/mlflow && \
    git checkout e226b6470db43c522bf00ca5e5a4cd7f51f83e5b && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/mlflow

RUN mkdir -p /logs/verifier
