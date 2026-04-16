FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Install uv for faster Python package management
RUN pip install uv

# Create log directory for verifier
RUN mkdir -p /logs/verifier

# Clone the langgraph repository at the base commit
# Using depth=100 to get enough history while keeping it lightweight
ARG BASE_COMMIT=890147681dd48a20b7ae139a423a9a74b9a9e2c3
RUN git clone --filter=blob:none --depth=100 https://github.com/langchain-ai/langgraph.git /workspace/langgraph && \
    cd /workspace/langgraph && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/langgraph/libs/checkpoint-conformance

# Install dependencies using uv
RUN uv pip install --system -e ".[test,lint]" || pip install -e ".[test,lint]"

# Set up pytest and other test tools
RUN pip install pytest pytest-asyncio

# Default working directory for the task
WORKDIR /workspace/langgraph
