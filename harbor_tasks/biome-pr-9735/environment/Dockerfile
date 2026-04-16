FROM rust:1.85-slim
WORKDIR /workspace

# Install build dependencies and python3 for pytest
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install just for running tests
RUN cargo install just

# Clone repository with the base commit
RUN git clone --filter=blob:none --depth=1 https://github.com/biomejs/biome.git biome_repo
WORKDIR /workspace/biome_repo
RUN git fetch --depth=1 origin 2d3f14390706b93b49469851081fd1e5ffaf45df && \
    git checkout 2d3f14390706b93b49469851081fd1e5ffaf45df

# Build dependencies and compile the parser crate (without running tests)
RUN cargo build -p biome_markdown_parser --release 2>/dev/null || cargo build -p biome_markdown_parser

WORKDIR /workspace
RUN mkdir -p /logs/verifier