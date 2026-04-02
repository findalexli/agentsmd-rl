FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git clone https://github.com/gradio-app/gradio.git /workspace/gradio && \
    cd /workspace/gradio && \
    git checkout 429a9fad5207fb27648d860a4802ff52a5b38746

# Install minimal deps (agent fills in specifics)
RUN pip install --no-cache-dir numpy 2>/dev/null || true
RUN pip install --no-cache-dir pytest pytest-json-ctrf ruff 2>/dev/null || true

# Install gradio from source for proper imports
RUN pip install --no-cache-dir -e /workspace/gradio 2>/dev/null || \
    pip install --no-cache-dir gradio-client pydantic httpx huggingface-hub tomlkit aiofiles anyio orjson markupsafe jinja2 pyyaml pillow ffmpy pydub python-multipart uvicorn fastapi starlette semantic-version 2>/dev/null || true

ENV PYTHONPATH="/workspace/gradio"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/gradio