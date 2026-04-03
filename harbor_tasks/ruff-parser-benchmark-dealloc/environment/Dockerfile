FROM rust:1.94-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@test.com" \
    && git config --global user.name "Agent"

# Clone repo at base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/ruff.git && \
    git fetch --depth=1 origin bd477d9535b5b83795e7eb42675faa8aa4fb954f && \
    git checkout FETCH_HEAD

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Fetch dependencies (cached in Docker layer)
RUN cargo fetch

# Pre-compile dependencies by checking the benchmark crate
# This caches all dep compilation so agent's test.sh only recompiles the changed crate
RUN cargo check -p ruff_benchmark --benches 2>&1 || true

WORKDIR /repo