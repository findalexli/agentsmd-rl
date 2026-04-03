FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone at exact base commit (before the fix)
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin 9a9997fd73c5eb29fb3677d3c489f5d3cd0765f6 && \
    git checkout FETCH_HEAD

# Install transformers with minimal deps (needed for check_repo.py imports)
RUN cd /workspace/transformers && pip install --no-cache-dir -e "." \
    && pip install --no-cache-dir ruff

ENV PYTHONPATH="/workspace/transformers/utils:/workspace/transformers/src:${PYTHONPATH}"

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers