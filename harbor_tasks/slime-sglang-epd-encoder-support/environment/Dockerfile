FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git clone https://github.com/THUDM/slime.git /workspace/slime && \
    cd /workspace/slime && \
    git checkout 5182e2d85c06827d57d0bbce98b5d39efeb5ae45

# Minimal deps — only what tests need (no torch/sglang/GPU libs)
RUN pip install --no-cache-dir pyyaml

ENV PYTHONPATH=/workspace/slime
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

RUN pip install --no-cache-dir aiohttp pytest pytest-json-ctrf

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime