FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (BEFORE the fix)
RUN git clone https://github.com/PrimeIntellect-ai/prime-rl.git /workspace && \
    cd /workspace && \
    git checkout b7afd84024531074830143d88bf0f60f506e1588 && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /workspace

ENV PYTHONPATH="/workspace/src:${PYTHONPATH}"