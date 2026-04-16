FROM python:3.12-slim

# Install git, make, and curl
RUN apt-get update && apt-get install -y git make curl && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

# Set up workspace
WORKDIR /workspace

# Clone the repository at base commit
RUN git clone --filter=blob:none https://github.com/langchain-ai/langgraph.git langgraph && \
    cd langgraph && \
    git checkout b8540449b477aeff563e8867378c3888516763b4

# Install Python SDK dependencies
WORKDIR /workspace/langgraph/libs/sdk-py
RUN pip install -e . && \
    pip install httpx orjson pytest

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
