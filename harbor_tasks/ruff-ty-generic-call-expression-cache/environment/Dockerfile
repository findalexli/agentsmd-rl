FROM rust:1.87-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Clone ruff at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin 64c4c96a57a525a36176f9b87dec0b7e7610abc3 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git user for agent commits
RUN git config user.email "agent@example.com" \
    && git config user.name "Agent"

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch

# Build ty binary (takes a while but saves agent time)
RUN CARGO_PROFILE_DEV_OPT_LEVEL=1 cargo build --bin ty 2>&1 | tail -5