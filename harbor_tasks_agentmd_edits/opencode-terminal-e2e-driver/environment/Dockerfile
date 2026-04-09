FROM node:22-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG=C.UTF-8

# Install dependencies for Bun, Python, and git
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git curl ca-certificates unzip python3 python3-pip build-essential && \
    rm -rf /var/lib/apt/lists/*

# Install Bun
RUN curl -fsSL https://bun.sh/install | bash
ENV PATH="/root/.bun/bin:${PATH}"

# Install pytest
RUN pip3 install pytest --break-system-packages

# Clone the repo at the base commit
RUN git clone --filter=blob:none https://github.com/anomalyco/opencode.git /workspace/opencode && \
    cd /workspace/opencode && \
    git checkout c9c0318e0e5c2fcd80fc1a32a1ccfe360f182f90 && \
    git config user.email "agent@test" && \
    git config user.name "Agent"

WORKDIR /workspace/opencode

# Verifier output directory
RUN mkdir -p /logs/verifier
