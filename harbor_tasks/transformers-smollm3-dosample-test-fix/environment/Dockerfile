FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Agent"

# Clone transformers at the base commit (parent of the merge commit)
RUN git clone https://github.com/huggingface/transformers.git /workspace/transformers && \
    cd /workspace/transformers && \
    git checkout 9cd278715c5154597a44110d6e0c114a7e90d6f5

# Install minimal deps for testing (no torch/GPU needed — tests are grep/AST based)
RUN cd /workspace/transformers && \
    pip install --no-cache-dir -e ".[quality]" 2>/dev/null || \
    pip install --no-cache-dir ruff

ENV PYTHONPATH=/workspace/transformers/src
RUN mkdir -p /logs/verifier

WORKDIR /workspace/transformers