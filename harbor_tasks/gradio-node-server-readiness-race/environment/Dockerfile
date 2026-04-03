FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before the fix)
RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin a35f5896e43d2585d9206e8256b4d7e321fcd0fe && \
    git checkout FETCH_HEAD

# No heavy deps needed — we only test the node_server.py module
# which uses stdlib (socket, http.client, time)
ENV PYTHONPATH="/workspace/gradio"
RUN pip install --no-cache-dir ruff
RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio