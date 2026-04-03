FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential pkg-config \
    python3 python3-pip python3-venv tmux \
    && rm -rf /var/lib/apt/lists/*

# Pre-install pytest so test.sh doesn't need to install at runtime
RUN pip3 install --break-system-packages pytest pytest-json-ctrf

# Clone uv at the buggy base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 5ad8577ff847d0bf115d45dd05a1efecf6fd797f && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git for potential commits
RUN git config user.email "test@test.com" && git config user.name "Test"

# Pre-fetch cargo dependencies to speed up test builds
RUN cargo fetch

# Pre-compile dependencies (not the crate itself) so cargo check is fast during tests
RUN cargo check -p uv-distribution 2>&1 || true