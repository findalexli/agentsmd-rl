FROM denoland/deno:debian-2.1.5

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install required system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates build-essential tmux python3 python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Install Node.js for syntax checking fallback
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Install Rust for cargo build support
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Clone repo at base commit (use --depth=1 for faster clone, full history not needed)
RUN git clone --depth=1 https://github.com/denoland/deno.git /workspace/deno && \
    cd /workspace/deno && \
    git fetch --depth=1 origin e6e72e57c2e2566b54f4672e03a6ff4d91d7b167 && \
    git checkout e6e72e57c2e2566b54f4672e03a6ff4d91d7b167 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/deno

# Pre-fetch cargo dependencies (optional, for faster builds during tests)
# Note: This may take a while and fail if the environment doesn't have all build deps
# We comment it out to keep the image build fast; cargo will fetch on demand
# RUN cargo fetch 2>&1 || true

# Verifier output directory (Harbor bind-mounts this)
RUN mkdir -p /logs/verifier
