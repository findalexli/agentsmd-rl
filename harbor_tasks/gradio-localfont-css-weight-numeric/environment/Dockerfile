FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global advice.detachedHead false

# Clone gradio at the base commit (before the fix)
RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin 0595d1b15ba6b7c47f68ddf7f79152b3d1d3c467 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio

# Install minimal deps for testing — only the gradio Python package
RUN pip install --no-cache-dir -e . 2>/dev/null || \
    pip install --no-cache-dir pyyaml toml pydantic httpx huggingface-hub aiofiles \
    jinja2 markupsafe orjson packaging pillow pydub python-multipart \
    starlette uvicorn fastapi typer rich semantic-version 2>/dev/null || true

# Set PYTHONPATH so we can import gradio modules
ENV PYTHONPATH=/workspace/gradio

RUN git config user.email "test@test.com" && git config user.name "Test"