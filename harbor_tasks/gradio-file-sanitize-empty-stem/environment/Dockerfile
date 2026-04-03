FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin f1cd0644d2608b493db07cd204c0831a111f9fb2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio

# Install only the gradio_client package (where the bug lives) + test deps
RUN pip install --no-cache-dir -e client/python/ \
    && pip install --no-cache-dir pytest pytest-json-ctrf

# Configure git for any patching
RUN git config user.email "test@test.com" && git config user.name "Test"

ENV PYTHONPATH=/workspace/gradio/client/python