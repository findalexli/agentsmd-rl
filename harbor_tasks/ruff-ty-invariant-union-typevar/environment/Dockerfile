FROM rust:1.93-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    CARGO_TERM_COLOR=never \
    CARGO_INCREMENTAL=0 \
    CARGO_NET_RETRY=10 \
    RUSTFLAGS="-C debuginfo=0" \
    CARGO_PROFILE_TEST_DEBUG=0 \
    CARGO_PROFILE_DEV_DEBUG=0

# Make Rust toolchain available to login shells (bash -lc resets PATH on Debian).
RUN echo 'export PATH="/usr/local/cargo/bin:$PATH"' > /etc/profile.d/rust.sh

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    ca-certificates \
    pkg-config \
    libssl-dev \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install pinned pytest for the test runner
RUN pip3 install --break-system-packages --no-cache-dir \
    pytest==8.3.4 \
    pytest-json-report==1.5.0

# Clone ruff at the base commit (parent of the merge commit for PR #24698)
RUN git clone --filter=blob:none https://github.com/astral-sh/ruff.git /workspace/ruff
WORKDIR /workspace/ruff
RUN git checkout ae613c5a55b35f9a96ce7d6f4e49b8aafc244d58

# Install nextest (matches the AGENTS.md recommended runner)
RUN cargo install --locked cargo-nextest@0.9.87

# Apply the mdtest fixture additions (these define the expected behavior the
# agent must implement). The fix to generics.rs is intentionally NOT applied.
COPY mdtest_patch.diff /tmp/mdtest_patch.diff
RUN git apply /tmp/mdtest_patch.diff && rm /tmp/mdtest_patch.diff

# Pre-build the mdtest binary at base commit so iteration is fast.
# This is the main cost-amortization step.
RUN cargo nextest run --no-run -p ty_python_semantic --test mdtest 2>&1 | tail -5

RUN mkdir -p /logs/verifier
