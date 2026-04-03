FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent"

# Clone repo at the base commit (before the fix)
ARG BASE_COMMIT=4f5a2944f0acfebba378e5b88bf2ab940f84b943
RUN git init /workspace/AReaL && \
    cd /workspace/AReaL && \
    git remote add origin https://github.com/inclusionAI/AReaL.git && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/AReaL

# No heavy deps needed — tests use AST parsing and direct function extraction.
# The repo imports torch/openai but our tests avoid importing those modules.
ENV PYTHONPATH=/workspace/AReaL