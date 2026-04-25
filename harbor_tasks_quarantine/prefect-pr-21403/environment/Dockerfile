FROM python:3.12-slim

WORKDIR /workspace

# Install git and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git curl build-essential && rm -rf /var/lib/apt/lists/*

# Clone the repository at the base commit
RUN git clone --filter=blob:none --depth=1 https://github.com/prefecthq/prefect.git /workspace/prefect
WORKDIR /workspace/prefect
RUN git fetch --filter=blob:none origin 19193fbca153190a7dc5861bb6501ba14771638a
RUN git checkout 19193fbca153190a7dc5861bb6501ba14771638a

# Install prefect in editable mode (this is required for imports to work)
RUN pip install --no-cache-dir -e .

# Install pytest and test dependencies
RUN pip install --no-cache-dir pytest==8.3.4 pytest-xdist==3.6.1 pytest-asyncio==0.24.0 respx opentelemetry-sdk

# Create logs directory
RUN mkdir -p /logs/verifier

# Copy test files
COPY tests/ /tests/
