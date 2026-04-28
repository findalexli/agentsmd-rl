FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

# Shallow clone — beam is a large monorepo
RUN git init /workspace/beam && \
    cd /workspace/beam && \
    git remote add origin https://github.com/apache/beam.git && \
    git fetch --depth=1 origin c8e45e79c699ef6df8847824833aeefab3b5767a && \
    git checkout FETCH_HEAD && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/beam

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages flake8 pycodestyle pylint yapf 2>/dev/null || pip install --no-cache-dir flake8 pycodestyle pylint yapf
