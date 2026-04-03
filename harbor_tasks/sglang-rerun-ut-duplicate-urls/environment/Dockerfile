FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at the base commit (BEFORE the fix)
ARG BASE_COMMIT=c580ddd19d613862b8720e307442946d0b9c41e2
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install only the deps needed for testing the slash command handler
RUN pip install --no-cache-dir PyGithub requests pyyaml pytest pytest-json-ctrf

# Configure git user for any patch operations
RUN git config --global user.email "test@test.com" && \
    git config --global user.name "Test"

ENV PYTHONPATH="/repo"