FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

ARG REPO=huggingface/transformers
ARG COMMIT=2cd52c267ce4d0212eaa40c0ec7192a11654336f

RUN git clone --filter=blob:none https://github.com/${REPO}.git /repo \
    && cd /repo \
    && git checkout ${COMMIT} \
    && git config user.email "test@test.com" \
    && git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install minimal deps for linting/AST checks only (no torch)
RUN pip install --no-cache-dir ruff

ENV PYTHONPATH=/repo/src