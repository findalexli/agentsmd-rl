FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at the buggy base commit (before the fix)
RUN git clone https://github.com/inclusionAI/AReaL.git /workspace/AReaL \
    && cd /workspace/AReaL \
    && git checkout 722e235a37e4a9f3e288e54629179befa494156b \
    && git config user.email "agent@test.local" \
    && git config user.name "Agent"

# Install only minimal deps needed for syntax checking / AST parsing
# No torch/GPU needed — tests are syntax and AST-based
RUN mkdir -p /logs/verifier

WORKDIR /workspace/AReaL

ENV PYTHONPATH="/workspace/AReaL:${PYTHONPATH:-}"