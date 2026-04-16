FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Copy the pre-cloned repository from the host
# The host needs to provide the openhands directory at /tmp/openhands-tmp
COPY openhands /workspace/openhands

# Install pytest and testing dependencies
RUN pip install pytest pytest-asyncio sqlalchemy aiosqlite tenacity stripe

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set Python path for imports
ENV PYTHONPATH="/workspace/openhands/enterprise:/workspace/openhands"
