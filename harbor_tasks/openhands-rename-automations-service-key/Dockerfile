FROM python:3.12-slim

WORKDIR /workspace

# Install git and dependencies
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/All-Hands-AI/OpenHands.git && \
    cd OpenHands && \
    git checkout 3516c3cdbe4e3713e7e1bb9b3b5041c281f29f0a

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/OpenHands
