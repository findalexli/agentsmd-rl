FROM python:3.12-slim

# Install git, curl, and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    build-essential \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone OpenHands at the base commit
ARG BASE_COMMIT=c9b2ce2fb9c61313d80643a489f81728bb9f5b09
RUN git clone --filter=blob:none https://github.com/OpenHands/OpenHands.git && \
    cd OpenHands && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/OpenHands

# Install the openhands package in editable mode with its dependencies
# First install pip packages that are commonly needed
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    pytest-mock \
    pydantic \
    fastapi \
    boto3 \
    botocore \
    httpx \
    aiofiles \
    pyyaml \
    python-dotenv \
    sqlalchemy \
    asyncpg \
    greenlet

# Install openhands in editable mode so imports work
RUN pip install -e . --no-deps 2>&1 || echo "Some dependencies may be missing, continuing..."

# Install poetry to resolve remaining deps
RUN pip install poetry --no-cache-dir && \
    poetry install --with test --no-interaction 2>&1 || echo "Poetry install may have some issues, continuing..."

# Create logs directory
RUN mkdir -p /logs/verifier

# Default command
CMD ["bash"]

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages ruff 2>/dev/null || pip install --no-cache-dir ruff
