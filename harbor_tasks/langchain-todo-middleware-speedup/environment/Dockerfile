FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Create workspace
WORKDIR /workspace

# Clone the langchain repository at base commit
RUN git clone --filter=blob:none https://github.com/langchain-ai/langchain.git /workspace/langchain \
    && cd /workspace/langchain \
    && git checkout 89cd0caa54d541e33ae87224c8e277bcbb026020

WORKDIR /workspace/langchain

# Install uv in the repo and set up dependencies
RUN cd libs/core && uv sync --all-groups
RUN cd libs/langchain_v1 && uv sync --all-groups

# Install pydantic explicitly (needed by core)
RUN pip install pydantic

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
