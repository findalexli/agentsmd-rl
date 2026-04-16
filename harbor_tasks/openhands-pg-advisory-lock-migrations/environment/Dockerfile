FROM python:3.12-slim

# Install git and required dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the OpenHands repository at the base commit
# Using filter=blob:none for faster clone
RUN git clone --filter=blob:none https://github.com/OpenHands/OpenHands.git

WORKDIR /workspace/OpenHands

# Checkout the base commit (parent of merge commit)
RUN git checkout 3268c299459b690337c89f858671329fd99f9b48

# Install enterprise dependencies
# First, install poetry
RUN pip install poetry

# Install enterprise dependencies (just enough for the migrations module)
WORKDIR /workspace/OpenHands/enterprise
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi || true

# Install additional required packages for testing
WORKDIR /workspace/OpenHands
RUN pip install sqlalchemy alembic pytest

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/OpenHands
