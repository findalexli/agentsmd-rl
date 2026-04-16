FROM rust:1.85-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip git curl zstd jq capnproto protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir --break-system-packages pytest pytest-xdist

WORKDIR /workspace

# Install cargo-nextest for faster test runs
RUN curl -L https://get.nexte.st/latest/linux | tar zx -C /usr/local/bin

# Clone turborepo with the base commit
RUN git clone --depth 1 https://github.com/vercel/turborepo.git turbo_repo
WORKDIR /workspace/turbo_repo
RUN git fetch --depth 1 origin e3b89b03ff7b9a34e0f4e25bb9e25ba76a171e77 && \
    git checkout e3b89b03ff7b9a34e0f4e25bb9e25ba76a171e77

WORKDIR /workspace/turbo_repo

# Pre-build to cache dependencies; continue even if build fails (tests will validate)
RUN cargo check -p turborepo-lib 2>&1 | tail -3 || true

RUN mkdir -p /logs/verifier
