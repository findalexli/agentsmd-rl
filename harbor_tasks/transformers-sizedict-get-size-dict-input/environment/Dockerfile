FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test User"

# Clone repo at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/huggingface/transformers.git /repo && \
    cd /repo && \
    git checkout a8683756653094e3fc3016df8abcdeaaec758f9a

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install transformers with minimal deps (no torch/GPU needed)
RUN pip install --no-cache-dir -e . numpy Pillow huggingface-hub 2>&1 | tail -5

# Copy test files

ENV PYTHONPATH=/repo/src