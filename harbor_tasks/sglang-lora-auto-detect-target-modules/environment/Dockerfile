FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone sglang at the base commit (before fix)
RUN git init /workspace/sglang && \
    cd /workspace/sglang && \
    git remote add origin https://github.com/sgl-project/sglang.git && \
    git fetch --depth=1 origin 9b29131961bb6c167e6956dae60a6269232ca694 && \
    git checkout FETCH_HEAD

# Install minimal deps for the LoRA module (no torch/GPU)
# We only need enough to parse the Python and run AST/import checks
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir \
    peft transformers safetensors pydantic \
    && pip install --no-cache-dir --no-deps -e /workspace/sglang/python

ENV PYTHONPATH="/workspace/sglang/python:${PYTHONPATH:-}"
RUN pip install --no-cache-dir pybase64

RUN mkdir -p /logs/verifier

WORKDIR /workspace/sglang

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages black isort ruff 2>/dev/null || pip install --no-cache-dir black isort ruff
