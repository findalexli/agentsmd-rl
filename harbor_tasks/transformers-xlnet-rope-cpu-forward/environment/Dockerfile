FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git clone https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout be6cf0848668852e3267d297211eb7e983e6c786

# Install minimal deps (agent fills in specifics)
RUN pip install --no-cache-dir numpy 2>/dev/null || true

RUN pip install --no-cache-dir ruff 2>/dev/null || true

ENV PYTHONPATH="/workspace/transformers"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/transformers
