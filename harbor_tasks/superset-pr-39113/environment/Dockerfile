# syntax=docker/dockerfile:1
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libffi-dev \
    libpq-dev \
    libsasl2-dev \
    libldap2-dev \
    libssl-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Clone Superset repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/superset.git superset \
    && cd superset \
    && git checkout fc8c06f7a3ba4c0a5feeafbb522b876b5f017d45

WORKDIR /workspace/superset

# Install superset-core package (has minimal dependencies)
RUN pip install --no-cache-dir -e ./superset-core

# Install additional dependencies needed for testing
RUN pip install --no-cache-dir \
    pytest \
    pytest-timeout \
    humanize \
    fastmcp \
    numpy \
    pandas \
    simplejson

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set PYTHONPATH to include superset source
ENV PYTHONPATH=/workspace/superset

CMD ["bash"]
