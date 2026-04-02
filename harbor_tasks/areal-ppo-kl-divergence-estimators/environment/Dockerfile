FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone AReaL at the base commit (before the fix)
RUN git clone https://github.com/inclusionAI/AReaL.git /workspace/AReaL \
    && cd /workspace/AReaL \
    && git checkout a0d122930f7de028404235688c7dba3f01854954 \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

# Install CPU-only torch for behavioral testing + pyyaml for judge
RUN pip install --no-cache-dir \
    torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir pyyaml

ENV PYTHONPATH=/workspace/AReaL
RUN mkdir -p /logs/verifier

WORKDIR /workspace/AReaL