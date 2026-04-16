FROM python:3.12-slim

# Install git, curl, and other build dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

# Set working directory
WORKDIR /workspace

# Clone the langchain repository at base commit (shallow clone for speed)
RUN git clone --filter=blob:none https://github.com/langchain-ai/langchain.git /workspace/langchain \
    && cd /workspace/langchain \
    && git checkout 8c15649127b3714b2b8f1903968163db70e6b90c

# Set working directory to the openai partner package
WORKDIR /workspace/langchain/libs/partners/openai

# Create logs directory for test results
RUN mkdir -p /logs/verifier

# Install dependencies using uv
RUN uv sync --group test

# Keep container running (tests will be mounted and run via test.sh)
CMD ["sleep", "infinity"]
