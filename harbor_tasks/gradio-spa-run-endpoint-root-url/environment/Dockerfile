FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the buggy commit (parent of fix PR #12894)
RUN git init /workspace/gradio \
    && cd /workspace/gradio \
    && git remote add origin https://github.com/gradio-app/gradio.git \
    && git fetch --depth=1 origin a8e6b7ba1e6af793b6a200d4cc6b07f3151f229e \
    && git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio

# Install gradio backend (needed for behavioral tests via TestClient)
RUN pip install --no-cache-dir -e . 2>&1 | tail -3 || true

RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"

ENV PYTHONPATH=/workspace/gradio
