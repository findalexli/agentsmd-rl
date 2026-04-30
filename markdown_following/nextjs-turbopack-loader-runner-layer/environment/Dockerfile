FROM python:3.12-slim

RUN rm -rf /var/lib/apt/lists/* && apt-get update && apt-get install -y \
    git curl ca-certificates build-essential tmux \
    && rm -rf /var/lib/apt/lists/*

# Install Rust toolchain (for cargo fmt / rustfmt checks)
RUN curl --proto '=https' --tlsv1.2 -sSf https://static.rust-lang.org/rustup/dist/x86_64-unknown-linux-gnu/rustup-init -o /tmp/rustup-init \
    && chmod +x /tmp/rustup-init \
    && /tmp/rustup-init -y --default-toolchain stable --component rustfmt --no-modify-path \
    && rm /tmp/rustup-init
ENV PATH="/root/.cargo/bin:${PATH}"

# Clone next.js at the base commit (before the fix)
# Use init+fetch to avoid downloading the default branch first (repo is very large)
RUN git init /workspace/next.js \
    && cd /workspace/next.js \
    && git remote add origin https://github.com/vercel/next.js.git \
    && git fetch --depth=1 origin b6ff1f6079694da08af88cec5cac7381e22cea10 \
    && git checkout FETCH_HEAD

RUN mkdir -p /logs/verifier

WORKDIR /workspace/next.js

# Configure git
RUN git config --global user.email "test@test.com" \
    && git config --global user.name "Test"