FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (before the fix)
RUN git init /workspace/sglang && \
    cd /workspace/sglang && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin d633ab7349a8cdfe939d25745c3f647c508b8be5 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang

# Install minimal deps needed for testing (no torch/GPU)
RUN pip install --no-cache-dir pyzmq psutil numpy

# Configure git user for agent commits
RUN git config --global user.email "agent@test.com" \
    && git config --global user.name "Agent"

ENV PYTHONPATH=/workspace/sglang/python:$PYTHONPATH