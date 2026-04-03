FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/AReaL && \
    cd /workspace/AReaL && \
    git remote add origin https://github.com/inclusionAI/AReaL.git && \
    git fetch --depth=1 origin 3142b88a5e93e991df727c81892d6cb8bd65d06e && \
    git checkout FETCH_HEAD

# Install minimal deps for test verification
RUN pip install --no-cache-dir numpy flask orjson aiohttp colorlog requests pydantic pyyaml psutil 2>/dev/null || true && \
    pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu 2>/dev/null || true

ENV PYTHONPATH="/workspace/AReaL"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/AReaL