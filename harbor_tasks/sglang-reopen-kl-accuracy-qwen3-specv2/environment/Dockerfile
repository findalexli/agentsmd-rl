FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (need enough depth to reach the commit)
RUN git clone --depth=500 https://github.com/sgl-project/sglang.git /workspace/sglang && \
    cd /workspace/sglang && \
    git fetch --depth=500 origin e9d92b0e33770651fd065c04ea28d0a5564e229d && \
    git checkout e9d92b0e33770651fd065c04ea28d0a5564e229d && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/sglang

# No heavy sglang dependencies needed - we use AST parsing for verification
# Install linting tools for repo checks
RUN pip install --no-cache-dir ruff black isort codespell

RUN mkdir -p /logs/verifier
