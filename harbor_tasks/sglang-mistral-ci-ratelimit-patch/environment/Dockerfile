FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin 33cca495ae75e745be62b5b009f4c87fb40dd044 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install minimal deps — only what we need for testing hf_transformers_utils.py
# The sglang package needs various deps; install base package in editable mode
RUN pip install --no-cache-dir -e "python/" 2>/dev/null || \
    pip install --no-cache-dir -e "python/[dev]" 2>/dev/null || \
    echo "Editable install attempted"

# Ensure PYTHONPATH includes the repo
ENV PYTHONPATH="/repo/python:${PYTHONPATH}"

# Configure git user for any patch operations
RUN git config user.email "test@test.com" && git config user.name "Test"
