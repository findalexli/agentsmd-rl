# Dockerfile for apache/superset#39099: Check pre-existing foreign keys on create util
FROM python:3.12-slim

# Install git and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone the repo at the base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/apache/superset.git /workspace/superset

WORKDIR /workspace/superset

# Checkout the base commit (parent of merge commit)
RUN git checkout a62be684a05278c026eccf5f2525f7ce605c9be8

# Install minimal dependencies needed for migration utilities
RUN pip install --no-cache-dir \
    alembic>=1.13.0 \
    sqlalchemy>=2.0.0 \
    pytest>=8.0.0 \
    pytest-timeout>=2.0.0

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/superset

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
