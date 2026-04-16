FROM python:3.12-slim

# Install git and dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set up working directory
WORKDIR /workspace

# Clone the OpenHands repo at base commit (shallow clone for efficiency)
ARG BASE_COMMIT=eb189144f2dfbbf0dad964cf7bdbd44e7910cb29
RUN git clone --filter=blob:none https://github.com/OpenHands/OpenHands.git && \
    cd OpenHands && \
    git fetch --depth=1 origin ${BASE_COMMIT} && \
    git checkout ${BASE_COMMIT}

# Install Poetry and pre-commit
RUN pip install poetry pre-commit

# Set up Python environment in the OpenHands directory
WORKDIR /workspace/OpenHands

# Install project dependencies (needed for imports to work in tests)
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --only main 2>&1 | tail -20 || \
    pip install pydantic httpx pytest pytest-asyncio

# Also install core deps directly if poetry fails
RUN pip install pydantic httpx anyio

# Create verifier logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]
