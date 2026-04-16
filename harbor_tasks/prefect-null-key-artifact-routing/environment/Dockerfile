FROM node:22-slim

# Install Python for pytest runner and git for cloning
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pytest
RUN pip3 install pytest --break-system-packages

# Create workspace
WORKDIR /workspace

# Clone the repo at the base commit (before the fix)
# Using filter=blob:none for faster clone
ARG BASE_COMMIT=c588fc30dc5a8bc136d411f37bfc7dda9e17cd78
RUN git clone --filter=blob:none https://github.com/prefecthq/prefect.git && \
    cd prefect && \
    git checkout ${BASE_COMMIT}

# Set working directory to the ui-v2 folder
WORKDIR /workspace/prefect/ui-v2

# Install dependencies
RUN npm ci

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
