# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential make && \
    rm -rf /var/lib/apt/lists/*

# Clone transformers repo at base commit
WORKDIR /workspace
RUN git init /workspace/&& && \
    cd /workspace/&& && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin 28af8184fb00a0e9bc778c3defdec39bbe7e8839 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/transformers

ENV PYTHONPATH="/workspace/transformers/src"

# Install dependencies needed for tests
RUN pip install --no-cache-dir \
    pytest pytest-json-ctrf \
    ruff tomli \
    numpy regex packaging requests filelock typing_extensions huggingface_hub safetensors

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
