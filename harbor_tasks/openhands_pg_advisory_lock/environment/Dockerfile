FROM python:3.10-slim

WORKDIR /workspace/gradio

# Install git and dependencies
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Clone gradio repo at the base commit (parent of 9953db9)
# This is the commit BEFORE the fix for filename sanitization
RUN git init /workspace/gradio && \
    cd /workspace/gradio && \
    git remote add origin https://github.com/gradio-app/gradio.git && \
    git fetch --depth=1 origin a35a24149fd5ef56d3faa3e1475b1f3cc6416cf6 && \
    git checkout FETCH_HEAD

# Install gradio dependencies
RUN pip install --no-cache-dir \
    numpy \
    pillow \
    pandas \
    requests \
    fastapi \
    pydantic \
    typing-extensions \
    aiofiles \
    httpx \
    websockets \
    pytest \
    pytest-asyncio \
    ruff

# Install the gradio_client from source
RUN pip install -e /workspace/gradio/client/python

# Install the main gradio package in development mode
RUN pip install -e /workspace/gradio

# Create test directories
RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio
