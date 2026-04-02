FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain (required for building ruff)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
ENV PATH="/root/.cargo/bin:${PATH}"

RUN mkdir -p /workspace /logs/verifier

WORKDIR /workspace

RUN git clone https://github.com/astral-sh/ruff.git /workspace/ruff && \
    cd /workspace/ruff && \
    git checkout b8fad8312fde560943653811ae3e16e22b99dfc7

ENV PYTHONPATH="/workspace/ruff"

RUN git config --global user.email "agent@test.com" && \
    git config --global user.name "Test Agent"

WORKDIR /workspace/ruff

# Pre-build ruff (debug) so the test environment has a binary ready.
# The gold solve.sh applies a one-file patch and rebuilds incrementally (~1-2 min).
RUN cargo build --bin ruff