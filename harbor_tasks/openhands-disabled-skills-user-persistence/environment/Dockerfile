FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Clone the OpenHands repository at base commit
ARG BASE_COMMIT=73ba66faeae1520fc2671b07677db4b5e3e235d3
RUN git clone --filter=blob:none https://github.com/OpenHands/OpenHands.git /workspace/OpenHands && \
    cd /workspace/OpenHands && \
    git checkout ${BASE_COMMIT}

# Set working directory to the repo
WORKDIR /workspace/OpenHands

# Install poetry and dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# Install enterprise dependencies if enterprise directory exists
RUN if [ -f enterprise/pyproject.toml ]; then \
    cd enterprise && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --with dev,test || true; \
    fi

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default working directory
WORKDIR /workspace/OpenHands
