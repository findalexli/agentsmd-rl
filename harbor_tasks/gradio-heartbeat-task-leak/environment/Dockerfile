FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/gradio-app/gradio.git /workspace/gradio \
    && cd /workspace/gradio \
    && git fetch --depth=1 origin b3722285163dcee97fe236e87d6ef98cee6be441 \
    && git checkout b3722285163dcee97fe236e87d6ef98cee6be441 \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio

# Tests are AST-only — no need to install gradio deps.
# Just need pytest and ruff for verification.
RUN pip install --no-cache-dir pytest pytest-json-ctrf ruff

ENV PYTHONPATH=/workspace/gradio
ENV GRADIO_ANALYTICS_ENABLED=false
