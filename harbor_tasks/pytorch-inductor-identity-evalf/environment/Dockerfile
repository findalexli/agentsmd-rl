FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git clone https://github.com/pytorch/pytorch.git /workspace/pytorch && \
    cd /workspace/pytorch && \
    git checkout f95d7a4bacff6a1e4f11a232c0f8a3f2b42bed4e

# Install minimal deps (agent fills in specifics)
RUN pip install --no-cache-dir numpy sympy 2>/dev/null || true

ENV PYTHONPATH="/workspace/pytorch"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/pytorch
