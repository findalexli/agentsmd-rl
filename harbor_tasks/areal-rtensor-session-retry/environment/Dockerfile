FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (BEFORE the fix)
RUN git clone https://github.com/inclusionAI/AReaL.git /repo && \
    cd /repo && \
    git checkout 9639749e700ea278e0617589391cc3dda6ec3a5c

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install minimal deps for testing (torch CPU-only, aiohttp, orjson)
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu && \
    pip install --no-cache-dir aiohttp orjson httpx colorlog numpy

ENV PYTHONPATH=/repo
RUN git config user.email "test@test.com" && git config user.name "Test"