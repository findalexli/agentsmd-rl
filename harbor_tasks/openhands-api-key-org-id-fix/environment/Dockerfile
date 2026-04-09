FROM python:3.12-slim

WORKDIR /workspace

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Clone the OpenHands repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=06cd53d752b022a7ae3676ab17c029f1f810c892
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git /workspace/openhands \
    && cd /workspace/openhands \
    && git fetch --depth=1 origin ${BASE_COMMIT} \
    && git checkout ${BASE_COMMIT}

# Install enterprise dependencies
WORKDIR /workspace/openhands/enterprise
RUN pip install --no-cache-dir poetry \
    && poetry config virtualenvs.create false \
    && poetry install --with dev,test --no-interaction

# Also install test dependencies that might be needed
RUN pip install --no-cache-dir pytest pytest-asyncio aiosqlite

# Create logs directory
RUN mkdir -p /logs/verifier

# Set working directory for tests
WORKDIR /workspace/openhands

# Set Python path
ENV PYTHONPATH=/workspace/openhands:/workspace/openhands/enterprise:$PYTHONPATH
