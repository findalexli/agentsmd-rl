FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/huggingface/transformers.git /repo && \
    cd /repo && \
    git checkout e6ed96c7e93a6408a151e3177793212b02b8bb53

RUN pip install --no-cache-dir ruff

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install transformers with base deps only (no torch/GPU) + pillow for image utils
RUN pip install --no-cache-dir -e . pillow ruff

RUN git config user.name "solver" && \
    git config user.email "solver@bench"

ENV PYTHONPATH=/repo/src