FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git init /workspace/vllm && \
    cd /workspace/vllm && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin 37a83007fef9925609a8d9b7c7b86bb41dab4e5d && \
    git checkout FETCH_HEAD

# Install minimal deps: torch CPU-only for weight_utils tests, ruff for lint
RUN pip install --no-cache-dir \
        torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir ruff

RUN mkdir -p /logs/verifier

WORKDIR /workspace/vllm

RUN git config user.email "test@test.com" && \
    git config user.name "Test"