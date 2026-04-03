FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (BEFORE the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin 9dc8d8aa3090ab3f39e6086d02b712f9274bc795 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install minimal deps (base transformers + tokenizers, no torch)
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pyyaml

# Configure git for potential agent commits
RUN git config --global user.email "agent@test.local" && \
    git config --global user.name "Agent"

ENV PYTHONPATH=/repo/src