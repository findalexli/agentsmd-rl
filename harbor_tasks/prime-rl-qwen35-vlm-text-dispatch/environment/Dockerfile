FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git init /repo
WORKDIR /repo
RUN git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git && \
    git fetch --depth 1 origin ecd080928014e20d1927a4f8b0b01d399151fdba && \
    git checkout FETCH_HEAD
RUN mkdir -p /logs/verifier

# Minimal deps for testing (CPU only — no GPU/CUDA)
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir transformers

ENV PYTHONPATH=/repo/src
RUN git config user.email "test@test.com" && git config user.name "Test"