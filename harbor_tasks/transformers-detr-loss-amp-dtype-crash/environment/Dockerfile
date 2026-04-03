FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin b94fee049373eb2e140d4866847559c4c42b3d7e && \
    git checkout FETCH_HEAD
RUN mkdir -p /logs/verifier

WORKDIR /repo
RUN git checkout b94fee049373eb2e140d4866847559c4c42b3d7e

# Install CPU-only torch (minimal) + deps needed by loss modules
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir scipy pillow numpy

# Install transformers from source (editable, no extras)
RUN pip install --no-cache-dir -e .

# Configure git for agent commits
RUN git config user.email "agent@test.local" && \
    git config user.name "Agent"

ENV PYTHONPATH="/repo/src:${PYTHONPATH}"