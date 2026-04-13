FROM python:3.11-slim

WORKDIR /workspace/requests

# Install git and make
RUN apt-get update && apt-get install -y git make && rm -rf /var/lib/apt/lists/*

# Copy the repo content (will be mounted at runtime, but we need the structure)
RUN mkdir -p /workspace/requests

# Install dependencies including those needed by requests
RUN pip install pytest pytest-httpbin httpbin pytest-cov pytest-mock trustme ruff urllib3 charset-normalizer idna certifi

# Set up working directory
WORKDIR /workspace/requests
