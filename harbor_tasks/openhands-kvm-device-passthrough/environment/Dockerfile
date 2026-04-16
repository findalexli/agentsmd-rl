FROM python:3.12-slim

# Install git and other dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone OpenHands repo at base commit
# Using filter=blob:none for faster clone
RUN git clone --filter=blob:none https://github.com/OpenHands/OpenHands.git /workspace/OpenHands && \
    cd /workspace/OpenHands && \
    git checkout b8f2932b023306926f8adc29d06621d1cf2e9432

# Install minimal Python dependencies needed for testing
# We only install what's needed to import and test the docker_sandbox_service module
RUN pip install --no-cache-dir \
    pytest \
    docker \
    pydantic \
    fastapi \
    httpx \
    pybase62 \
    openhands-agent-server==1.16.1

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Set working directory to the repo
WORKDIR /workspace/OpenHands

# Set PYTHONPATH so openhands module can be imported
ENV PYTHONPATH=/workspace/OpenHands

# Default command
CMD ["bash"]
