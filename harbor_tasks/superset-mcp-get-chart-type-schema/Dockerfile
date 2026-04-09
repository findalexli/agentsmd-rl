# Apache Superset MCP Service - get_chart_type_schema tool task
FROM python:3.12-slim

WORKDIR /workspace

# Install git and dependencies
RUN apt-get update && apt-get install -y \
    git \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=8e811de5643022a97f6cb1890aa513197b7312e4
RUN git clone --filter=blob:none --depth=100 https://github.com/apache/superset.git superset && \
    cd superset && \
    git checkout ${BASE_COMMIT}

# Install Python dependencies (minimal for MCP service testing)
WORKDIR /workspace/superset
RUN pip install --no-cache-dir \
    pydantic>=2.0.0 \
    pytest \
    pytest-mock \
    "fastmcp>=2.0.0" \
    -e .

# Create log directory
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace
