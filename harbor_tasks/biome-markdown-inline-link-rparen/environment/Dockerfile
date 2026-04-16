FROM rust:1.85-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest --break-system-packages --quiet

RUN mkdir -p /logs/verifier

WORKDIR /workspace/biome

# Clone with depth=1 for faster clone
RUN git clone --depth 1 https://github.com/biomejs/biome.git /workspace/biome

WORKDIR /workspace/biome

# Checkout the base commit (before the fix)
RUN git fetch --depth 1 origin 1dd4a560a567d0a47784f9d5014ee8bc073b6912
RUN git checkout 1dd4a560a567d0a47784f9d5014ee8bc073b6912

# Pre-build to cache dependencies (optional, helps with faster test runs)
RUN cargo build --release -p biome_markdown_parser 2>/dev/null || true
