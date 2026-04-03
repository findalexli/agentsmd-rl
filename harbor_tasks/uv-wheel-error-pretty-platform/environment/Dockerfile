FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    pkg-config libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 202e0f083180c36907ee7fbb5bdf7707722a9521 && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git
RUN git config user.email "test@test.com" && git config user.name "Test"

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch 2>/dev/null || true