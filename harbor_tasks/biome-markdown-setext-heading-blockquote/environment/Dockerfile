FROM rust:1.85-slim

# Install build essentials and just
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install just (biome uses justfile)
RUN curl -fsSL https://github.com/casey/just/releases/download/1.39.0/just-1.39.0-x86_64-unknown-linux-musl.tar.gz | tar xz -C /usr/local/bin --strip-components=1

# Clone biome (shallow)
WORKDIR /workspace
RUN git clone --depth 1 --filter=blob:none https://github.com/biomejs/biome.git

WORKDIR /workspace/biome
# Checkout base commit
RUN git fetch --depth 1 origin e021c4a308ee89f6009f200de5056435080c7179 && git checkout e021c4a308ee89f6009f200de5056435080c7179

# Install python3 and pytest (needed by test harness)
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    && pip install --break-system-packages pytest \
    && rm -rf /var/lib/apt/lists/*

# Create log directory
RUN mkdir -p /logs/verifier

# Pre-build to cache dependencies
RUN cargo build --release -p biome_markdown_parser 2>/dev/null || true

# Set default command
CMD ["/bin/bash"]