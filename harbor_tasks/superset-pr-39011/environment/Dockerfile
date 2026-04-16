# Dockerfile for superset-mcp-dashboard-draft task
FROM python:3.12-slim

# Install git and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    pkg-config \
    libpq-dev \
    default-libmysqlclient-dev \
    libsasl2-dev \
    libldap2-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone repository with filter for efficiency
RUN git clone --filter=blob:none https://github.com/apache/superset.git /workspace/superset

# Checkout base commit (parent of merge)
WORKDIR /workspace/superset
RUN git checkout 25eea295f6c9e8060619beccb267dd9c7628f882

# Install minimal dependencies for the schema test
# We need pydantic and humanize (direct imports in schemas.py)
RUN pip install --no-cache-dir \
    pydantic>=2.8.0 \
    humanize \
    pytest

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/superset
