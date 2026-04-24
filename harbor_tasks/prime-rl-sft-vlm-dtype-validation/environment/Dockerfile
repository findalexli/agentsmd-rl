FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent"

# Clone repo at the base commit (before the fix)
RUN git init /workspace/prime-rl && \
    cd /workspace/prime-rl && \
    git remote add origin https://github.com/PrimeIntellect-ai/prime-rl.git && \
    git fetch --depth=1 origin 7ef29a76600d767e732c99c8eaaec768830a7bca && \
    git checkout FETCH_HEAD

# Install minimal deps needed for config validation tests
# pydantic + pydantic-config (samsja fork) for BaseConfig, transformers for VLM utils
RUN pip install --no-cache-dir \
    pydantic \
    pydantic-settings \
    "pydantic-config @ git+https://github.com/samsja/pydantic_config.git@1562882463aed6fca1964a1ae0aa4b5141f89d73" \
    tyro \
    tomli-w \
    transformers \
    && rm -rf /root/.cache/pip

# Make the package importable
ENV PYTHONPATH="/workspace/prime-rl/src:${PYTHONPATH:-}"

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir pytest pytest-json-ctrf

RUN mkdir -p /logs/verifier

WORKDIR /workspace/prime-rl

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
