FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 python3-pip \
    pkg-config libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone repo at base commit (before fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 96f329b8d2ab82245b86beb0be835dcbd7be254a && \
    git checkout FETCH_HEAD

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git
RUN git config user.email "test@test.com" && git config user.name "Test"

# Pre-fetch and pre-compile cargo dependencies to speed up test builds
RUN cargo fetch 2>/dev/null || true
RUN cargo build -p uv-torch --tests 2>/dev/null || true