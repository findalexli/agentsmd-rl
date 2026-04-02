FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (before the fix)
RUN git clone https://github.com/sgl-project/sglang.git /workspace && \
    cd /workspace && \
    git checkout 6047d2c690483224b2bb7d70288ea60b0b8e0c7d && \
    git config user.email "agent@test.local" && \
    git config user.name "Agent"

# Install only the minimal deps needed for test.sh (AST parsing, no torch/GPU)
# ci_register.py is pure Python with no external deps beyond stdlib
ENV PYTHONPATH="/workspace/python:${PYTHONPATH}"

RUN mkdir -p /logs/verifier

WORKDIR /workspace