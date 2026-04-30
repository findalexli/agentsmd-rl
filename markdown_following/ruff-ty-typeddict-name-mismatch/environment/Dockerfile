FROM rust:1.94-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git \
        ca-certificates \
        pkg-config \
        libssl-dev \
        build-essential \
        curl \
        patch \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Ensure cargo is on PATH for login shells (bash -lc), since /etc/profile
# hardcodes PATH without /usr/local/cargo/bin.
RUN echo 'export PATH="/usr/local/cargo/bin:$PATH"' > /etc/profile.d/rust.sh

RUN pip3 install --break-system-packages --no-cache-dir \
        pytest==8.4.0

WORKDIR /workspace

RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git ruff \
 && cd ruff \
 && git checkout ca3343e4cf25e8314c26cce2031abb67ed6a3b16

WORKDIR /workspace/ruff

RUN cargo build --release --bin ty -p ty

ENV TY_BIN=/workspace/ruff/target/release/ty

RUN mkdir -p /logs/verifier
