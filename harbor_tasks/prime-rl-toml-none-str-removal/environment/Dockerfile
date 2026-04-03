FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git init /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git && \
    git fetch --depth=1 origin 4f612601f6447b3df1ee17e535ac698b5cc3d16c && \
    git checkout FETCH_HEAD

# Install only the minimal deps needed for testing (no torch/vllm)
RUN pip install --no-cache-dir pydantic tomli_w

ENV PYTHONPATH=/workspace/prime-rl/src
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prime-rl