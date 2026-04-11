FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Sparse checkout: only the yaml examples + agent config (full repo is ~8 GB)
RUN mkdir -p /workspace/beam && cd /workspace/beam && \
    git init && \
    git remote add origin https://github.com/apache/beam.git && \
    git sparse-checkout init && \
    git sparse-checkout set sdks/python/apache_beam/yaml/examples/ .agent/ && \
    git fetch --depth=1 origin b9d48fa1750f6427cb86fa1de9d52e4d1849a433 && \
    git checkout b9d48fa1750f6427cb86fa1de9d52e4d1849a433 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/beam

# Install pyyaml for test_outputs.py
RUN pip install --no-cache-dir pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
