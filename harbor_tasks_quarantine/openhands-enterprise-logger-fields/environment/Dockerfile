FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Clone the OpenHands repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout 8f87ef59c72f1c7bae2b937164caf99731ac8e83

# Set working directory to enterprise
WORKDIR /workspace/OpenHands/enterprise

# Install poetry and dependencies
RUN pip install poetry && \
    poetry config virtualenvs.in-project true && \
    poetry install --with dev,test --no-interaction

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default to enterprise directory
WORKDIR /workspace/OpenHands/enterprise
