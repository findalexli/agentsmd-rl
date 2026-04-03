FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone vllm at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/vllm-project/vllm.git && \
    git fetch --depth=1 origin a8eab8f30dda380a67c515c743365840b4347ccd && \
    git checkout FETCH_HEAD

# Configure git user for agent commits
RUN cd /repo && \
    git config user.email "agent@example.com" && \
    git config user.name "Agent"

# No heavy deps needed — tests use AST analysis (vllm needs torch + compiled C ops)
# Install only minimal Python packages for testing
RUN pip install --no-cache-dir pytest pytest-json-ctrf

ENV PYTHONPATH=/repo
RUN mkdir -p /logs/verifier

WORKDIR /repo