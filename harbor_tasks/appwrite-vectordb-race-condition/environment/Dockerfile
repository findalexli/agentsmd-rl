FROM php:8.3-cli-slim

# Install git and python3 for testing
RUN apt-get update && apt-get install -y \
    git \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repository at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/appwrite/appwrite.git appwrite && \
    cd appwrite && \
    git checkout a5b0378138a6097e256a8d9553a18b892b6ba9ea

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
