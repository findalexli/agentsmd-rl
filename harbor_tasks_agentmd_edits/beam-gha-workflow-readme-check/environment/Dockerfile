FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Sparse checkout: only .github/ and .agent/ (full repo is ~8 GB)
RUN mkdir -p /workspace/beam && cd /workspace/beam && \
    git init && \
    git remote add origin https://github.com/apache/beam.git && \
    git sparse-checkout init && \
    git sparse-checkout set .github/ .agent/ && \
    git fetch --depth=1 origin ae6d624c2b6d1fed15e4e96bf40e707808ad652b && \
    git checkout ae6d624c2b6d1fed15e4e96bf40e707808ad652b && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/beam

# Install pyyaml for test_outputs.py (parses YAML workflow files)
RUN pip install --no-cache-dir pyyaml

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
