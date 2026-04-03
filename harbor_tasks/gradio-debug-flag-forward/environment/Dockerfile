FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before the fix)
RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin 4d97c68f8a5a55ba686ab5ce599b932b51754984 && \
    git checkout FETCH_HEAD

# Install minimal deps for testing (just gradio core, no heavy extras)
RUN cd /workspace/gradio \
    && pip install --no-cache-dir -e "." 2>&1 | tail -5 \
    && pip install --no-cache-dir ruff

ENV PYTHONPATH=/workspace/gradio
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir numpy Pillow pytest-json-ctrf

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio