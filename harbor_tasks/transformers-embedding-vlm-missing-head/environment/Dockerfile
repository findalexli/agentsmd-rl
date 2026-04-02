FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before the fix)
RUN git clone https://github.com/huggingface/transformers.git /workspace/repo
RUN mkdir -p /logs/verifier

WORKDIR /workspace/repo
RUN git checkout 05514c4bb641ba1537d17048fd93f50f45d5f19d

# Install CPU-only torch (smaller) and transformers in dev mode
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -e .

# Configure git for applying patches
RUN git config user.email "test@test.com" && git config user.name "Test"

ENV PYTHONPATH=/workspace/repo/src
WORKDIR /workspace/repo