FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit
RUN git clone --filter=blob:none https://github.com/apache/superset.git /workspace/superset && \
    cd /workspace/superset && \
    git checkout 81c4b126e9f7c3d0533dbc15a90b8d45db106a87

WORKDIR /workspace/superset

# Install Python dependencies from the repo's requirements
RUN pip install --no-cache-dir -r /workspace/superset/requirements/base.txt \
    pytest fastmcp humanize 'pydantic>=2.0' 2>&1 | tail -20

# Create logs directory
RUN mkdir -p /logs/verifier
