FROM python:3.12-slim

WORKDIR /workspace

# Install git and dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone the repo at base commit (shallow clone for speed)
RUN git clone --depth=100 --filter=blob:none https://github.com/apache/superset.git /workspace/superset && \
    cd /workspace/superset && \
    git fetch --depth=100 origin a62be684a05278c026eccf5f2525f7ce605c9be8 && \
    git checkout a62be684a05278c026eccf5f2525f7ce605c9be8

# Install Python dependencies needed for testing
RUN cd /workspace/superset && \
    pip install --no-cache-dir -e ".[testing]" sqlalchemy alembic pytest

# Create verifier log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/superset
