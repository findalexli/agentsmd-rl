FROM python:3.12-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the OpenHands repository at base commit
ARG BASE_COMMIT=a458c9b785a1b016e9f8c4e190a0fd9960c6e58e
RUN git clone --filter=blob:none https://github.com/OpenHands/OpenHands.git openhands && \
    cd openhands && \
    git checkout ${BASE_COMMIT}

# Install Python dependencies needed for testing
RUN pip install pytest fastapi pydantic starlette

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/openhands
