FROM python:3.12-slim

WORKDIR /workspace

# Install git and basic deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clone dagster repo with depth=1
RUN git clone --filter=blob:none --depth=1 https://github.com/dagster-io/dagster.git dagster-io_dagster

WORKDIR /workspace/dagster-io_dagster

# Checkout the base commit (parent of merge commit)
RUN git fetch --depth=1 origin 7f73da5a70984fdcbf6b79967ccfd2bdd86acdeb && git checkout 7f73da5a70984fdcbf6b79967ccfd2bdd86acdeb

# Install python deps for testing
RUN pip install --no-cache-dir pytest==8.3.4

# Create logs directory
RUN mkdir -p /logs/verifier

# No COPY of solution/ or tests/ - harness mounts them

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
