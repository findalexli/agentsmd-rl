FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux && \
    rm -rf /var/lib/apt/lists/*

# Clone vllm at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/vllm-project/vllm.git /workspace && \
    cd /workspace && \
    git checkout b9dbc5c4ab2b01f626376ffaeb68e575e70ff58c

# Install torch CPU-only (needed to test tensor operations)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Set PYTHONPATH so vllm modules are importable
ENV PYTHONPATH=/workspace

# Configure git for applying patches
RUN cd /workspace && \
    git config user.email "test@test.com" && \
    git config user.name "Test"

RUN mkdir -p /logs/verifier

WORKDIR /workspace