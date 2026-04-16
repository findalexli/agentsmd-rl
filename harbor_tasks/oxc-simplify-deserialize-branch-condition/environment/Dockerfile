FROM rust:1.85-slim-bookworm

# Install system dependencies and Node.js
RUN apt-get update && apt-get install -y \
    git \
    curl \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install pnpm and pytest
RUN npm install -g pnpm
RUN pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest --user 2>/dev/null || pip install pytest

# Clone the repository at the base commit
ARG BASE_COMMIT=9f494c3bc888b77a22a9994b6246efdbbe762235
RUN git clone --filter=blob:none https://github.com/oxc-project/oxc.git /workspace/oxc && \
    cd /workspace/oxc && \
    git checkout ${BASE_COMMIT}

# Set working directory
WORKDIR /workspace/oxc

# Install Rust components needed
RUN rustup component add clippy rustfmt

# Install cargo tools
RUN cargo install cargo-insta typos-cli cargo-shear ast-grep --locked || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Pre-fetch dependencies to speed up builds
RUN cargo fetch || true

WORKDIR /workspace/oxc
