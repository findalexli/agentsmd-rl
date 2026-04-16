FROM python:3.12-slim

# Install git and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    make \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Clone the repo at base commit
WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/langchain-ai/langchain.git
WORKDIR /workspace/langchain
RUN git checkout 050b779d97d4c72dfea1c46bfc12b1049be3ab63

# Set up the ollama package
WORKDIR /workspace/langchain/libs/partners/ollama

# Install the package into system Python with all dependencies
RUN pip install -e . && pip install pytest pytest-asyncio ruff

# Create verifier logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace/langchain
