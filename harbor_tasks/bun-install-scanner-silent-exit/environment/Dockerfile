FROM node:22-bookworm

RUN apt-get -o Acquire::Check-Valid-Until=false -o Acquire::AllowInsecureRepositories=true \
    -o Acquire::AllowDowngradeToInsecureRepositories=true update \
    && apt-get -o APT::Get::AllowUnauthenticated=true install -y --no-install-recommends \
    git curl ca-certificates build-essential tmux python3 \
    && rm -rf /var/lib/apt/lists/*

# Install bun for running JS tests
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Clone bun repo at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/oven-sh/bun.git /workspace/bun \
    && cd /workspace/bun \
    && git fetch --depth 1 origin 1d50d640f8fec6ce2d144f0cfd204e30da373c64 \
    && git checkout 1d50d640f8fec6ce2d144f0cfd204e30da373c64

RUN mkdir -p /logs/verifier

WORKDIR /workspace/bun

# Configure git user for agent commits
RUN git config user.name "agent" && git config user.email "agent@test.local"

# Tests and rubric are volume-mounted at runtime