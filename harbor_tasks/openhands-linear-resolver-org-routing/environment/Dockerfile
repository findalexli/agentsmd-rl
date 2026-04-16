FROM python:3.12-slim

WORKDIR /workspace

# Install git and dependencies needed for cloning and running tests
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry and uv
RUN pip install poetry uv

# Clone the OpenHands repo at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git OpenHands && \
    cd OpenHands && \
    git checkout e46bcfa82ff82ce6ad21a4349fa2da9b8860f3a4

WORKDIR /workspace/OpenHands

# Install enterprise dependencies (needed for tests)
RUN cd enterprise && poetry install --with dev,test --no-interaction --no-root || true

# Create logs directory
RUN mkdir -p /logs/verifier

# Set environment variables for testing
ENV PYTHONPATH=.:$PYTHONPATH
ENV PYTHONUNBUFFERED=1
