FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

ARG BASE_COMMIT=7b00e3ba398d355d5f277a4896743b16f21049eb
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /repo \
    && cd /repo \
    && git checkout $BASE_COMMIT

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install transformers in editable mode (minimal — no torch/GPU deps)
RUN pip install --no-cache-dir -e ".[testing]" \
    && pip install --no-cache-dir ruff

# Configure git user for any commits agents might make
RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"

ENV PYTHONPATH="/repo/src:${PYTHONPATH:-}"