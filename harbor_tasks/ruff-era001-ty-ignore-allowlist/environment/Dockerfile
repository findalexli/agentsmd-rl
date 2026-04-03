FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone ruff at the base commit (before fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin 55c5d90699afabf3e01340b7ff8e645fe4a237a2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for agent use
RUN git config user.email "agent@example.com" \
    && git config user.name "Agent"

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch