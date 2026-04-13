FROM rust:1.82-slim-bookworm

# Install required dependencies
RUN apt-get update && apt-get install -y \
    git \
    pkg-config \
    libssl-dev \
    curl \
    make \
    gcc \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pytest for running tests
RUN pip3 install pytest --break-system-packages 2>/dev/null || pip3 install pytest

# Install Rust components needed for checks
RUN rustup component add rustfmt clippy

# Clone the ruff repository at a specific commit
WORKDIR /workspace
RUN git clone --depth 1 https://github.com/astral-sh/ruff.git ruff

WORKDIR /workspace/ruff

# INTENTIONALLY BREAK: Create formatting issues and clippy warnings
# These will be fixed by solve.sh to demonstrate fail-to-pass testing
RUN echo 'pub fn badly_formatted(  ) { let unused=1; }' > /tmp/bad_code.rs && \
    cat /tmp/bad_code.rs >> crates/ruff_python_parser/src/lib.rs

# Pre-build to cache dependencies (optional, speeds up later cargo commands)
# This step can be skipped if we want faster Docker build times
# RUN cargo fetch

# Set environment variables for consistent output
ENV CARGO_TERM_COLOR=never
ENV RUST_BACKTRACE=0

# Default command just echoes the repo path
CMD ["echo", "/workspace/ruff"]
