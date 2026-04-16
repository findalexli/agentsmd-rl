FROM python:3.12-slim

WORKDIR /workspace

# Install git and dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone the OpenHands repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=54858c0fc02196f797e4bb411eb00bc12267b0cc
RUN git clone --filter=blob:none --depth=100 https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git fetch --depth=100 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/OpenHands

# Install Python dependencies (minimal set for testing)
# The repo uses poetry but we'll install key deps directly for faster setup
RUN pip install --no-cache-dir \
    fastapi \
    pydantic \
    pytest \
    httpx \
    starlette \
    pytest-asyncio

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
