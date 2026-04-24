# Benchmark task environment for apache/superset PR #39207
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    libffi-dev \
    libssl-dev \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Clone repository with blob filter for efficiency
RUN git clone --filter=blob:none https://github.com/apache/superset.git /workspace/superset

WORKDIR /workspace/superset

# Checkout base commit (parent of merge commit)
RUN git checkout 4c2dd634643e34f56ae698887dfc9d5bee8a6851

# Install minimal Python dependencies needed for testing
# Focus on core backend deps only - skip frontend/UI deps
RUN pip install --no-cache-dir \
    flask \
    flask-appbuilder \
    sqlalchemy \
    pandas \
    numpy \
    jinja2 \
    markupsafe \
    pyyaml \
    humanize \
    pytz \
    python-dateutil \
    sqlalchemy-utils \
    "marshmallow>=3.18.0,<4.0.0" \
    sqlglot \
    pytest \
    pytest-timeout

# Install the superset package in editable mode (minimal install)
# This allows importing superset modules for testing
RUN pip install --no-cache-dir -e . --no-deps || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory
WORKDIR /workspace/superset

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
