FROM python:3.12-slim

# Install git and dependencies
RUN apt-get update && apt-get install -y \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /workspace

# Clone the repo at base commit (shallow clone with filter for efficiency)
RUN git clone --filter=blob:none --depth=100 https://github.com/All-Hands-AI/OpenHands.git openhands && \
    cd openhands && \
    git fetch --depth=1 origin ff240c968bb938e414cacaa1b31be4f2948c4619 && \
    git checkout ff240c968bb938e414cacaa1b31be4f2948c4619

# Set working directory to enterprise
WORKDIR /workspace/openhands/enterprise

# Install enterprise dependencies (only what's needed for testing)
RUN pip install --no-cache-dir \
    pytest \
    pytest-asyncio \
    sqlalchemy[asyncio] \
    aiosqlite \
    stripe \
    pydantic \
    email-validator \
    tenacity \
    httpx \
    python-json-logger \
    uuid6

# Create logs directory for verifier
RUN mkdir -p /logs/verifier
