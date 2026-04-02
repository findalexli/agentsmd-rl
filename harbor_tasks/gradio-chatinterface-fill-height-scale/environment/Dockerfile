FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone gradio at the base commit (before the fix)
RUN git clone https://github.com/gradio-app/gradio.git /workspace/gradio \
    && cd /workspace/gradio \
    && git checkout bb127c74bd6301e3782e0ce4744161ae976a8481 \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

# Install minimal deps for testing (no frontend build needed)
RUN cd /workspace/gradio && pip install --no-cache-dir -e ".[dev]" 2>&1 | tail -5

ENV PYTHONPATH=/workspace/gradio
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install --no-cache-dir numpy Pillow

RUN pip install --no-cache-dir ruff

RUN mkdir -p /logs/verifier

WORKDIR /workspace/gradio