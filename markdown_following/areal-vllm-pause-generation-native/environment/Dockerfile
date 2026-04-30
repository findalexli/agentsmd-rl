FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
ARG REPO=https://github.com/inclusionAI/AReaL.git
ARG COMMIT=45e805ba8d274ec2c3cbb0699658449c2c6e163a

RUN git clone --depth=1 --filter=blob:none "$REPO" /workspace/AReaL && \
    cd /workspace/AReaL && \
    git checkout "$COMMIT" && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

# No heavy deps needed — tests are AST/source-level only
# (vllm is not importable without GPU, and we only inspect the source file)
RUN pip install --no-cache-dir pytest pytest-json-ctrf pyyaml ruff

RUN mkdir -p /logs/verifier

WORKDIR /workspace/AReaL
ENV PYTHONPATH="/workspace/AReaL:${PYTHONPATH:-}"
