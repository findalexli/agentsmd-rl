FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone AReaL at the base commit (before the fix)
RUN git init /workspace/AReaL && \
    cd /workspace/AReaL && \
    git remote add origin https://github.com/inclusionAI/AReaL.git && \
    git fetch --depth=1 origin a0d122930f7de028404235688c7dba3f01854954 && \
    git checkout FETCH_HEAD

# Install CPU-only torch for behavioral testing + pyyaml for judge
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir pyyaml

ENV PYTHONPATH=/workspace/AReaL
RUN mkdir -p /logs/verifier

WORKDIR /workspace/AReaL

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
