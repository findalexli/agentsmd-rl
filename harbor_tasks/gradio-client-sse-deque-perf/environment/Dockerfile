FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before the fix)
RUN git clone https://github.com/gradio-app/gradio.git /workspace/gradio \
    && cd /workspace/gradio \
    && git checkout 83b223b746c3933920dfef670e545a12de9177ed \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

# Install gradio_client and its dependencies (minimal — no full gradio)
RUN cd /workspace/gradio && pip install --no-cache-dir ./client/python/

ENV PYTHONPATH=/workspace/gradio/client/python
RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio