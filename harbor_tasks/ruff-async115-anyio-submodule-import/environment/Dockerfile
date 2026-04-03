FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone ruff at the base commit (before fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin 6c8101a5b3ca4a6833f93e93cf8a33ea83f88616 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for agent use
RUN git config user.email "agent@example.com" \
    && git config user.name "Agent"

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch