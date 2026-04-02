FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

ARG REPO=huggingface/transformers
ARG COMMIT=f5e573080ae0838799c1f9a0ba28be8431120b56

RUN git clone --filter=blob:none https://github.com/${REPO}.git /repo && \
    cd /repo && \
    git checkout ${COMMIT} && \
    git config user.email "bench@test" && \
    git config user.name "Bench"

# Install transformers (editable) + torch CPU-only for testing
RUN cd /repo && \
    pip install --no-cache-dir -e ".[quality]" && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /repo
ENV PYTHONPATH=/repo/src