FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/mlflow/mlflow.git /workspace/mlflow && \
    cd /workspace/mlflow && \
    git checkout bc59a546e39cd15f9ae92d32a3766b0892c40007 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/mlflow

# Install JS dependencies for type checking
WORKDIR /workspace/mlflow/mlflow/server/js
RUN yarn install --frozen-lockfile 2>&1 || yarn install 2>&1 || true

WORKDIR /workspace/mlflow

# Verifier output directory
RUN mkdir -p /logs/verifier
