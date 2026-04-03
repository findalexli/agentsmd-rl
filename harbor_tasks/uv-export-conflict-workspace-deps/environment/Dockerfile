FROM rust:1.86-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential pkg-config \
    python3 python3-pip tmux \
    && rm -rf /var/lib/apt/lists/*

# Clone uv at the buggy base commit (parent of merge commit e169f431)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 3d4cb95c809aef28c4c527435948c0aae5c2f3d2 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for potential commits
RUN git config user.email "test@test.com" && git config user.name "Test"

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch

# Pre-compile the resolver crate's dependencies so cargo check is fast
RUN cargo check -p uv-resolver 2>&1 || true