FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Clone the repo at base commit (before the fix)
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout a65ddc3db6294cd6f1e0a56a849603ecad85a338

WORKDIR /workspace/OpenHands

# Install poetry and dependencies needed for testing
RUN pip install poetry pytest pytest-asyncio

# Install minimal dependencies (only what's needed for the test)
# We only need the openhands package and its core dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --only main --no-root || true

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
