FROM rust:1.86-slim-bookworm

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux pkg-config python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Pre-install pytest so tests don't need network at runtime
RUN pip3 install --break-system-packages pytest pytest-json-ctrf

# Clone uv at the base commit (before the fix)
RUN git init /repo && \
    cd /repo && \
    git remote add origin https://github.com/astral-sh/uv.git && \
    git fetch --depth=1 origin 685a79876028a83976acafffd94e8abe3295d72a && \
    git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /repo

# Configure git
RUN git config user.name "test" && git config user.email "test@test.com"

# Pre-fetch cargo dependencies to speed up builds
RUN cargo fetch 2>/dev/null || true

# Pre-compile at base commit so agent changes only need incremental rebuild
RUN cargo check -p uv 2>/dev/null || true