FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git clone https://github.com/inclusionAI/AReaL.git /repo \
    && cd /repo \
    && git checkout f6556e88582e82b747ab1ac4038af2e106a464ee \
    && git config user.email "agent@test.com" \
    && git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Install minimal deps for testing (no torch/GPU — tests use AST + mock)
RUN pip install --no-cache-dir pytest pytest-json-ctrf

# Copy test harness

ENV PYTHONPATH="/repo"