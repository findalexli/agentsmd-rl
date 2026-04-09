FROM python:3.12-slim

# Install git and other required dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone the OpenHands repository at base commit (shallow clone for speed)
ARG BASE_COMMIT=c9b2ce2fb9c61313d80643a489f81728bb9f5b09
RUN git clone --filter=blob:none --depth=50 https://github.com/All-Hands-AI/OpenHands.git /workspace/openhands \
    && cd /workspace/openhands \
    && git checkout ${BASE_COMMIT}

# Set working directory
WORKDIR /workspace/openhands

# Install poetry and dependencies needed for testing
RUN pip install poetry pytest pytest-asyncio

# Install only the dependencies needed for the aws_event_service tests
# boto3, pydantic, fastapi, sqlalchemy, httpx
RUN pip install boto3 pydantic fastapi botocore sqlalchemy httpx

# Create log directories
RUN mkdir -p /logs/verifier

# Set environment variables
ENV PYTHONPATH=/workspace/openhands:$PYTHONPATH
