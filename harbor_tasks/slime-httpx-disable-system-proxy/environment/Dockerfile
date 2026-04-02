FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git clone https://github.com/THUDM/slime.git /workspace/slime && \
    cd /workspace/slime && \
    git checkout e46e660059b5f2ae949ad812c7d49af823f415a3

# Install minimal deps
RUN pip install --no-cache-dir numpy httpx 2>/dev/null || true

ENV PYTHONPATH="/workspace/slime"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/slime