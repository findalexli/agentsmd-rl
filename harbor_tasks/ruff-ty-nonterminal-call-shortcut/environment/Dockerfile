FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone ruff at the base commit (before fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin 7973118f777bee32466a4fdb54f0816268f942ea && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for agent use
RUN git config user.email "agent@example.com" \
    && git config user.name "Agent"

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch

# Pre-build ty so incremental rebuilds after agent changes are fast
RUN cargo build --bin ty 2>&1 || true