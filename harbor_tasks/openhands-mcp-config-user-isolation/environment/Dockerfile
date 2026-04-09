FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    sqlalchemy \
    alembic \
    pydantic \
    pydantic-settings

# Set up workspace
WORKDIR /workspace
ENV REPO_DIR=/workspace/OpenHands

# Clone the OpenHands repo at the base commit
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git ${REPO_DIR}
WORKDIR ${REPO_DIR}
RUN git checkout f7b53283b5692e1ba1755bfba8a51f09c76f5ec7

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /testbed
