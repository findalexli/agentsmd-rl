FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Install test dependencies (numpy + pandas for eval_utils)
RUN pip install --no-cache-dir numpy pandas pyyaml pytest pytest-json-ctrf

# Clone repo at base commit (BEFORE the fix)
# Use --filter=blob:none for faster clone (fetches blobs on demand)
RUN git clone --filter=blob:none https://github.com/PrimeIntellect-ai/prime-rl.git /workspace \
    && cd /workspace \
    && git checkout 18594ab2f5c43bdf80424731e5e268d67311056e \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

ENV PYTHONPATH="/workspace/src:${PYTHONPATH}"
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /workspace