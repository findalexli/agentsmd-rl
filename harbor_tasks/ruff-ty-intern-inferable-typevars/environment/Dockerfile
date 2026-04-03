FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone ruff at the base commit (before fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin 3a44cce48e2f9687c767a36b9af2da280ef68c64 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for agent use
RUN git config user.email "agent@example.com" \
    && git config user.name "Agent"

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch

# Warm the build cache — compile the full workspace so incremental builds are fast
RUN CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo check -p ty_python_semantic 2>&1 || true