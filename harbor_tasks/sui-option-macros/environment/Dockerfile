FROM python:3.12-slim

# Install git and basic tools
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace/sui

# Clone the repository at the base commit
ARG BASE_COMMIT=63cb7f767409e0589a9d5265e55a727cb8a020b5
RUN git clone --filter=blob:none --no-checkout https://github.com/MystenLabs/sui.git . && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install pytest
RUN pip install pytest

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
