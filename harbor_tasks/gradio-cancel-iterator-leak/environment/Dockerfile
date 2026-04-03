FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin 0a0378dee463fb10e5a95685d595801171cf641b && \
    git checkout FETCH_HEAD

WORKDIR /workspace/gradio

# Install gradio from source (with all deps) plus test tooling
RUN pip install --no-cache-dir -e . && \
    pip install --no-cache-dir pytest pytest-json-ctrf ruff

ENV PYTHONPATH="/workspace/gradio"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"