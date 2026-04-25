FROM python:3.12-slim

WORKDIR /workspace

# Install git and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Clone the repo at base commit
RUN git clone --filter=blob:none https://github.com/langchain-ai/langgraph.git && \
    cd langgraph && \
    git checkout c965a483e8b37f73bc7136801e2d8da199597285

# Install langgraph dependencies
WORKDIR /workspace/langgraph/libs/langgraph
RUN pip install -e ".[dev]" --no-cache-dir && \
    pip install pytest redis uv --no-cache-dir

# Create logs directory
RUN mkdir -p /logs/verifier

WORKDIR /workspace
