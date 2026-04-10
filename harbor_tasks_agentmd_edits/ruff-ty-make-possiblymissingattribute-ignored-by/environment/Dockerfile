FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

RUN apt-get update &&     apt-get install -y --no-install-recommends         git curl ca-certificates build-essential tmux pkg-config libssl-dev libclang-dev &&     rm -rf /var/lib/apt/lists/*

# Install Rust toolchain (rustup) with required components
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain none
ENV PATH="/root/.cargo/bin:$PATH"

# Install specific Rust toolchain version and components needed for CI
RUN rustup toolchain install 1.93 && rustup default 1.93
RUN rustup component add clippy rustfmt

# Install cargo-nextest for faster test execution
RUN cargo install cargo-nextest --locked

# Clone repo at base commit
RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git /workspace/ruff &&     cd /workspace/ruff &&     git checkout 74c7fe849fdfe8b79e8e8e031e5e7b3673be3f4a &&     git config user.email "agent@test" &&     git config user.name "Agent"

WORKDIR /workspace/ruff

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
