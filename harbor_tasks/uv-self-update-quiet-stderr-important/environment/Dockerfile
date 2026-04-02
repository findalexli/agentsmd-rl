FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (BEFORE the fix)
RUN git clone --filter=blob:none https://github.com/astral-sh/uv.git /repo \
    && cd /repo \
    && git checkout 262a50bb4c952cf2461d4073ae21081ed516f21c

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git user for any commits the agent needs
RUN git config user.name "Agent" && git config user.email "agent@test.com"

# No heavy build step — tests extract and compile minimal Rust snippets