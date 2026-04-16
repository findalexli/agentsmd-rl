FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# Install git for cloning
RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the langchain repo at the base commit
RUN git clone --filter=blob:none https://github.com/langchain-ai/langchain.git

# Checkout the base commit
WORKDIR /workspace/langchain
RUN git checkout 342d8bdef21c957471cdf9dc9c6af59e3d70d9e7

# Install Python dependencies using uv
# Sync only what's needed for testing
RUN uv sync --group test --group lint || true

# Create log directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
