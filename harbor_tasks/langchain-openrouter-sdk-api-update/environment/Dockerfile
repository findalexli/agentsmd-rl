FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for dependency management (used by langchain monorepo)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Create workspace
WORKDIR /workspace

# Clone the langchain repository
RUN git clone --filter=blob:none https://github.com/langchain-ai/langchain.git

# Set working directory to the openrouter package
WORKDIR /workspace/langchain/libs/partners/openrouter

# Checkout the base commit (before the fix)
RUN git checkout 64bbcef37e7733f7029f57af644635bddad8e30a

# Install the package dependencies using uv
# The base version has openrouter==0.7.11 which has the old API
RUN uv sync --all-groups

# Create logs directory for test results
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
