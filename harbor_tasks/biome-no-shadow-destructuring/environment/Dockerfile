FROM rust:1.93.1-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
ENV CARGO_TERM_COLOR=never
ENV RUST_BACKTRACE=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    git=1:2.39.* \
    ca-certificates \
    pkg-config \
    libssl-dev \
    build-essential \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages \
    pytest==8.3.4 \
    pytest-json-report==1.5.0

# Fix bash -lc: /etc/profile hardcodes a PATH without /usr/local/cargo/bin.
# Copy the rustup env shim to /etc/profile.d so login shells source it.
RUN cp /usr/local/cargo/env /etc/profile.d/rust.sh

WORKDIR /workspace

RUN git init /workspace/biome && \
    cd /workspace/biome && \
    git remote add origin https://github.com/biomejs/biome.git && \
    git fetch --depth=1 origin 4509fc654f90cc007689c9e46bc3d172016ae039 && \
    git checkout FETCH_HEAD

WORKDIR /workspace/biome

# Pre-place test fixture files (these belong to the gold patch's test suite,
# but we need them present so the spec_tests macro discovers them at compile
# time. Without these, snapshot tests can't run at all.)
COPY fixtures/invalidDestructuring.js     /workspace/biome/crates/biome_js_analyze/tests/specs/nursery/noShadow/invalidDestructuring.js
COPY fixtures/invalidDestructuring.js.snap /workspace/biome/crates/biome_js_analyze/tests/specs/nursery/noShadow/invalidDestructuring.js.snap
COPY fixtures/validDestructuring.js        /workspace/biome/crates/biome_js_analyze/tests/specs/nursery/noShadow/validDestructuring.js
COPY fixtures/validDestructuring.js.snap   /workspace/biome/crates/biome_js_analyze/tests/specs/nursery/noShadow/validDestructuring.js.snap

# Install rustfmt so cargo fmt --check works inside the container.
RUN rustup component add rustfmt

# Build test binaries (and all transitive deps) once during image build.
# This is the long pole; subsequent agent edits get incremental rebuilds.
RUN cargo test --no-run -p biome_js_analyze --test spec_tests 2>&1 | tail -50

RUN mkdir -p /logs/verifier
