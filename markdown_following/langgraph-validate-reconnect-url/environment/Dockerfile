FROM python:3.12-slim

# Install git, make, and curl
RUN apt-get update && apt-get install -y git make curl && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv /root/.local/bin/uv /usr/local/bin/uv

# Set up workspace
WORKDIR /workspace

# Clone the repository at base commit
RUN git init /workspace/langgraph && \
    cd /workspace/langgraph && \
    git remote add origin https://github.com/langchain-ai/langgraph.git && \
    git fetch --depth=1 origin b8540449b477aeff563e8867378c3888516763b4 && \
    git checkout FETCH_HEAD

# Install Python SDK dependencies
WORKDIR /workspace/langgraph/libs/sdk-py
RUN pip install -e . && \
    pip install httpx orjson pytest

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
