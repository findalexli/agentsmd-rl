FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone slime at base commit (before the fix)
RUN git clone https://github.com/THUDM/slime.git /workspace/slime \
    && cd /workspace/slime \
    && git checkout 6e3699c83ac65c119e755ccec1a14ac87644489f

# Configure git
RUN cd /workspace/slime && \
    git config user.email "agent@test.com" && \
    git config user.name "Agent"

RUN mkdir -p /logs/verifier

WORKDIR /workspace/slime