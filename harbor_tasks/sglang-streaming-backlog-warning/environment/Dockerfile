FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin 4dd4e06f1d5fd1d294cb82a84b803256760cbfff && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for potential patch application
RUN git config user.email "agent@test.local" && git config user.name "Agent"

# Install minimal deps — only what's needed for testing the tokenizer_manager module
# We do NOT install torch/GPU deps; tests use AST/grep checks on the source
RUN pip install --no-cache-dir pydantic aiohttp requests fastapi uvicorn psutil numpy

ENV PYTHONPATH="/repo/python:${PYTHONPATH:-}"