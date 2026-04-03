FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone vllm at the base commit (BEFORE the fix)
ARG BASE_COMMIT=0aac2048bf3a7e60eaddf1ebcb4165ed777eb8ff
RUN git init /workspace/vllm && \
    cd /workspace/vllm && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

# Configure git for potential patch operations
RUN cd /workspace/vllm && \
    git config user.email "agent@test.local" && \
    git config user.name "Agent"

# Install minimal deps for testing (no torch/GPU needed — tests use AST analysis)
# Only install what test.sh needs to parse Python files
RUN pip install --no-cache-dir pyyaml

ENV PYTHONPATH=/workspace/vllm
RUN mkdir -p /logs/verifier

WORKDIR /workspace/vllm