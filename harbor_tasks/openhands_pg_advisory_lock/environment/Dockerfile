FROM python:3.12-slim

# Install git and dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Create logs directory
RUN mkdir -p /logs/verifier

# Clone the repository at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout 3268c299459b690337c89f858671329fd99f9b48

# Install minimal Python dependencies for testing
RUN pip install pytest pyyaml sqlalchemy alembic

WORKDIR /workspace/OpenHands
