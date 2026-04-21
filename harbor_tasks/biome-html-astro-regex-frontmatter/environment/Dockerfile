FROM rust:1.85-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    git \
    make \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --break-system-packages pytest

WORKDIR /workspace

# Clone and checkout base commit directly
# Use full clone to ensure we can reach any commit
RUN git clone --depth=1 --filter=blob:none https://github.com/biomejs/biome.git biome_repo && \
    cd biome_repo && \
    git fetch origin 467fd87daec3d8c1fe64850a82480364480b313e && \
    git checkout 467fd87daec3d8c1fe64850a82480364480b313e

RUN mkdir -p /logs/verifier

# Pre-build to cache dependencies (from /workspace/biome_repo)
WORKDIR /workspace/biome_repo
RUN cargo build -p biome_html_parser --release 2>/dev/null || true

ENV RUST_BACKTRACE=1