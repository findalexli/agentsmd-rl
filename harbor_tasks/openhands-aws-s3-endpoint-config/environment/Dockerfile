FROM python:3.12-slim

WORKDIR /workspace

# Install git
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Clone OpenHands repo at base commit (shallow clone for speed)
RUN git init /workspace/openhands && \
    cd /workspace/openhands && \
    git remote add origin https://github.com/All-Hands-AI/OpenHands.git && \
    git fetch --depth=1 origin c9b2ce2fb9c61313d80643a489f81728bb9f5b09 && \
    git checkout FETCH_HEAD

# Install core Python testing dependencies
RUN pip install --no-cache-dir pytest pytest-asyncio

# Install runtime dependencies needed for the target module to be importable
RUN pip install --no-cache-dir boto3 botocore pydantic fastapi

# Install the openhands package in editable mode (ignore errors for optional deps)
RUN cd /workspace/openhands && pip install --no-cache-dir -e . 2>/dev/null || true

# Install linting, type-checking, and their stubs
RUN pip install --no-cache-dir mypy ruff validate-pyproject
RUN pip install --no-cache-dir types-requests types-setuptools types-pyyaml types-toml types-docker types-Markdown lxml 2>/dev/null || true

# Create log directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/openhands
