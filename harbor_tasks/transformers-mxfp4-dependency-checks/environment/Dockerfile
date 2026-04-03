FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git init /workspace/transformers && \
    cd /workspace/transformers && \
    git remote add origin https://github.com/huggingface/transformers.git && \
    git fetch --depth=1 origin a8732d5546d84bfb4519b6dbf461c947a5de45f6 && \
    git checkout FETCH_HEAD

# Install minimal deps for quantizer testing (torch CPU + accelerate needed by validate_environment)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir accelerate numpy ruff pytest pytest-json-ctrf 2>/dev/null || true

# Install transformers from source so imports work properly
RUN pip install --no-cache-dir -e /workspace/transformers 2>/dev/null || true

ENV PYTHONPATH="/workspace/transformers/src"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/transformers