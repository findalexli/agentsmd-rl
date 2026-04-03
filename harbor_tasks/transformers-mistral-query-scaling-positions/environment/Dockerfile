FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (before fix)
ARG BASE_COMMIT=e94695e574f969ba5eeb8e442a7fb1e9f72ff37f
RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers

# Install minimal deps for testing (no torch/GPU — we test the scaling function with pure torch CPU)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pyyaml pytest pytest-json-ctrf

# Configure git for potential commits
RUN git config user.email "test@test.com" && \
    git config user.name "Test"

ENV PYTHONPATH=/workspace/transformers/src