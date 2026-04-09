FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the OpenHands repository at base commit
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout b8f2932b023306926f8adc29d06621d1cf2e9432

WORKDIR /workspace/OpenHands

# Install Python dependencies (only what's needed for testing)
RUN pip install pytest pydantic docker httpx pybase62 fastapi

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set environment variables for testing
ENV PYTHONPATH=/workspace/OpenHands:$PYTHONPATH
