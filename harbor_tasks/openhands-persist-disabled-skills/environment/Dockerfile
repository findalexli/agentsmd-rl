FROM python:3.12-slim

# Install git and basic dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /workspace

# Clone OpenHands repo at base commit (shallow clone for speed)
ARG BASE_COMMIT=73ba66faeae1520fc2671b07677db4b5e3e235d3
RUN git clone --filter=blob:none --no-checkout https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git sparse-checkout init --cone && \
    git sparse-checkout set enterprise storage openhands && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install Python dependencies for testing
RUN pip install pytest sqlalchemy alembic pydantic jinja2 cryptography pyjwt requests fastapi litellm

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the repo
WORKDIR /workspace/OpenHands
