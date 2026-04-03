FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before the fix)
RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin 30af84cdd100855999281de8720cbb6d58b48556 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio

# Install test dependencies (YAML parsing + pytest runner)
RUN pip install --no-cache-dir pyyaml pytest pytest-json-ctrf

ENV PYTHONPATH=/workspace/gradio
