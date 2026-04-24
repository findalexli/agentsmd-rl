FROM python:3.12-slim

WORKDIR /workspace

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    make \
    && rm -rf /var/lib/apt/lists/*

# Clone the repository at base commit
ARG REPO=All-Hands-AI/OpenHands
ARG BASE_COMMIT=0c5e30ab33a2286821df5b5012abc2345a9002ce

RUN git clone --filter=blob:none https://github.com/${REPO}.git openhands && \
    cd openhands && \
    git checkout ${BASE_COMMIT}

WORKDIR /workspace/openhands

# Install Python dependencies for testing
# Core dependencies from the repo
RUN pip install pytest pytest-asyncio httpx fastapi pydantic jinja2 sqlalchemy

# Install openhands package dependencies (if pyproject.toml exists)
RUN cd /workspace/openhands && \
    if [ -f pyproject.toml ]; then \
        pip install -e . 2>/dev/null || true; \
    fi

# Install additional dependencies that may be needed
RUN pip install aiohttp aiodocker pyyaml tomli toml litellm

# Create logs directory for verifier
RUN mkdir -p /logs/verifier

# Keep container running for tests
CMD ["bash"]

# auto-installed (scaffold Change 2A retrofit 2026-04-24)
RUN pip install --no-cache-dir --break-system-packages mypy ruff 2>/dev/null || pip install --no-cache-dir mypy ruff
