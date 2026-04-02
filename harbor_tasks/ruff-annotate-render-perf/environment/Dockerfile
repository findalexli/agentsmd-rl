FROM rust:1.85-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Configure git
RUN git config --global user.email "agent@test.com" \
    && git config --global user.name "Agent"

# Clone repo at base commit (before the fix)
RUN git clone --no-checkout https://github.com/astral-sh/ruff.git /repo \
    && cd /repo \
    && git checkout e7f1c536715d8a44aa830c1e4947e2ffcca06e0e

RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Fetch dependencies (cached in Docker layer)
RUN cargo fetch

# Pre-compile the annotate_snippets crate and its deps so incremental builds are fast
RUN cargo check -p ruff_annotate_snippets 2>&1 || true

WORKDIR /repo